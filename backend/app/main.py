from __future__ import annotations

import hashlib
import base64
import io
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import qrcode

from app.grading import analyze_card, crop_preview, rotate_image_bytes
from app.identification import identify_card_candidates
from app.pricing import get_prices

app = FastAPI(title="DeckFlow Demo API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_BYTES = 10 * 1024 * 1024

CARD_PROFILES = {
    "charizard-ex-223": {"card_name": "Charizard ex", "set_name": "Obsidian Flames", "card_number": "223/197", "variant": "Special Illustration Rare", "raw_market_price": 48.25, "graded_market_price": 90.00},
    "pikachu-160": {"card_name": "Pikachu", "set_name": "Crown Zenith", "card_number": "160/159", "variant": "Secret Rare", "raw_market_price": 14.80, "graded_market_price": 38.00},
    "umbreon-vmax-215": {"card_name": "Umbreon VMAX", "set_name": "Evolving Skies", "card_number": "215/203", "variant": "Alternate Art Secret", "raw_market_price": 1280.00, "graded_market_price": 1850.00},
}


class Defect(BaseModel):
    category: str
    result: str
    severity: str


class Assessment(BaseModel):
    assessment_id: str
    created_at: str
    card_name: str
    set_name: str
    card_number: str
    variant: str
    estimated_grade: float
    grade_range: str
    confidence: float
    condition: str
    centering: str
    defects: list[Defect]
    raw_market_price: float
    graded_market_price: float
    recommendation: str
    selling_window: str
    pricing_source: str
    identification_mode: str
    is_official_grade: bool
    processing_ms: int
    front_preview: str
    back_preview: str
    crop_status: str
    card_candidates: list[dict] = []


class CropResult(BaseModel):
    preview: str
    boundary_detected: bool


class MobileSession(BaseModel):
    session_id: str
    upload_url: str
    qr_data_url: str | None = None
    status: str
    front_received: bool
    back_received: bool
    front_preview: str | None = None
    back_preview: str | None = None
    upload_count: int = 0


class CandidatePriceRequest(BaseModel):
    card_name: str
    set_name: str
    card_number: str
    variant: str
    justtcg_id: str | None = None
    estimated_grade: float
    condition: str


ASSESSMENT_HISTORY: list[Assessment] = []
MOBILE_SESSIONS: dict[str, dict] = {}


async def read_image(upload: UploadFile, side: str) -> bytes:
    if upload.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"The {side} file must be a JPG, PNG, or WEBP image.")
    data = await upload.read()
    if len(data) < 100:
        raise HTTPException(status_code=400, detail=f"The {side} image is empty or too small. Please capture it again.")
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=400, detail=f"The {side} image exceeds 10 MB.")
    return data


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "DeckFlow Demo API"}


@app.get("/api/public-url")
async def public_url() -> dict[str, str]:
    configured = os.getenv("DECKFLOW_PUBLIC_URL", "").strip().rstrip("/")
    if configured:
        return {"url": configured}
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get("http://cloudflared:2000/quicktunnel")
            response.raise_for_status()
            hostname = response.json().get("hostname", "").strip()
        if hostname:
            return {"url": f"https://{hostname}"}
    except (httpx.HTTPError, ValueError, TypeError):
        pass
    raise HTTPException(status_code=503, detail="The secure phone link is still starting.")


@app.get("/api/cards")
def supported_cards() -> list[dict]:
    return [{"id": key, **value} for key, value in CARD_PROFILES.items()]


@app.get("/api/assessments", response_model=list[Assessment])
def assessment_history() -> list[Assessment]:
    return list(reversed(ASSESSMENT_HISTORY[-20:]))


def _session_response(session: dict, include_qr: bool = False) -> MobileSession:
    return MobileSession(
        session_id=session["session_id"], upload_url=session["upload_url"],
        qr_data_url=session.get("qr_data_url") if include_qr else None,
        status="ready" if session.get("front") and session.get("back") else "waiting",
        front_received=bool(session.get("front")), back_received=bool(session.get("back")),
        front_preview=session.get("front_preview"), back_preview=session.get("back_preview"),
        upload_count=int(session.get("upload_count", 0)),
    )


@app.post("/api/mobile-sessions", response_model=MobileSession)
def create_mobile_session(public_base_url: Annotated[str, Form()]) -> MobileSession:
    base = public_base_url.strip().rstrip("/")
    if not base.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Enter a full laptop address beginning with http:// or https://.")
    session_id = uuid.uuid4().hex[:10]
    upload_url = f"{base}/?mobile_session={session_id}"
    qr = qrcode.make(upload_url)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_data_url = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")
    session = {"session_id": session_id, "upload_url": upload_url, "qr_data_url": qr_data_url, "created_at": time.time(), "upload_count": 0}
    MOBILE_SESSIONS[session_id] = session
    return _session_response(session, include_qr=True)


@app.get("/api/mobile-sessions/{session_id}", response_model=MobileSession)
def mobile_session_status(session_id: str) -> MobileSession:
    session = MOBILE_SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="This phone-upload session expired or does not exist.")
    return _session_response(session, include_qr=True)


@app.post("/api/mobile-sessions/{session_id}/upload", response_model=MobileSession)
async def upload_mobile_photos(
    session_id: str,
    front: Annotated[UploadFile, File(description="Card front")],
    back: Annotated[UploadFile, File(description="Card back")],
) -> MobileSession:
    session = MOBILE_SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="This phone-upload session expired or does not exist.")
    front_data = await read_image(front, "front")
    back_data = await read_image(back, "back")
    try:
        front_preview, _ = crop_preview(front_data)
        back_preview, _ = crop_preview(back_data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    session.update({"front": front_data, "front_type": front.content_type, "back": back_data, "back_type": back.content_type, "front_preview": front_preview, "back_preview": back_preview, "upload_count": int(session.get("upload_count", 0)) + 1})
    return _session_response(session)


@app.get("/api/mobile-sessions/{session_id}/image/{side}")
def mobile_session_image(session_id: str, side: str) -> Response:
    session = MOBILE_SESSIONS.get(session_id)
    if not session or side not in {"front", "back"} or not session.get(side):
        raise HTTPException(status_code=404, detail="That uploaded card image is not available.")
    return Response(content=session[side], media_type=session.get(f"{side}_type") or "image/jpeg")


@app.post("/api/candidate-price")
async def candidate_price(selection: CandidatePriceRequest) -> dict:
    profile = selection.model_dump(exclude={"estimated_grade", "condition"})
    raw, graded, source = await get_prices({**profile, "condition": selection.condition}, selection.estimated_grade)
    return {**profile, "raw_market_price": raw, "graded_market_price": graded, "pricing_source": source}


@app.post("/api/crop", response_model=CropResult)
async def crop_card(
    image: Annotated[UploadFile, File(description="Photo containing one trading card")],
    rotation: Annotated[int, Form()] = 0,
) -> CropResult:
    data = await read_image(image, "card")
    try:
        data = rotate_image_bytes(data, rotation)
        preview, found = crop_preview(data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return CropResult(preview=preview, boundary_detected=found)


@app.post("/api/assessments", response_model=Assessment)
async def create_assessment(
    front: Annotated[UploadFile, File(description="Front image of a trading card")],
    back: Annotated[UploadFile, File(description="Back image of a trading card")],
    card_id: Annotated[str, Form()] = "charizard-ex-223",
    card_hint: Annotated[str, Form()] = "",
    front_rotation: Annotated[int, Form()] = 0,
    back_rotation: Annotated[int, Form()] = 0,
) -> Assessment:
    started = time.perf_counter()
    front_bytes = await read_image(front, "front")
    back_bytes = await read_image(back, "back")
    front_bytes = rotate_image_bytes(front_bytes, front_rotation)
    back_bytes = rotate_image_bytes(back_bytes, back_rotation)
    if card_id not in CARD_PROFILES:
        raise HTTPException(status_code=400, detail="That demo fallback card is not supported.")
    fallback_profile = CARD_PROFILES.get(card_id, CARD_PROFILES["charizard-ex-223"])

    digest = hashlib.sha256(front_bytes + back_bytes).hexdigest()
    try:
        vision = analyze_card(front_bytes, back_bytes)
        front_preview, front_found = crop_preview(front_bytes)
        back_preview, back_found = crop_preview(back_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not front_found or not back_found:
        missing = "front and back" if not front_found and not back_found else "front" if not front_found else "back"
        raise HTTPException(
            status_code=422,
            detail=f"DeckFlow could not isolate the full {missing} card boundary. Lay the card flat on a plain dark surface, keep every edge visible, and scan again.",
        )
    grade = vision.grade
    candidate_profiles, identification_mode = await identify_card_candidates(front_bytes, card_hint)
    identified = candidate_profiles[0] if candidate_profiles else None
    if identified:
        profile = {**fallback_profile, **identified}
    elif card_hint.strip():
        profile = fallback_profile
    else:
        profile = {"card_name": "Identification uncertain", "set_name": "Retake or enter card name", "card_number": "Unknown", "variant": "No confident match", "raw_market_price": 0.0, "graded_market_price": 0.0}
    if not identified:
        identification_mode += "; no unrelated match was accepted—retake or enter the card name/number"
    raw_price, graded_price, pricing_source = await get_prices({**profile, "condition": vision.condition}, grade)
    profile_data = {**profile, "raw_market_price": raw_price, "graded_market_price": graded_price}
    low = max(1, grade - 0.5)
    high = min(10, grade + 0.5)
    assessment = Assessment(
        assessment_id=f"DF-{digest[:10].upper()}",
        created_at=datetime.now(timezone.utc).isoformat(),
        **profile_data,
        estimated_grade=grade,
        grade_range=f"{low:g}-{high:g}",
        confidence=vision.confidence,
        condition=vision.condition,
        centering=vision.centering,
        defects=[Defect(**item) for item in vision.defects],
        recommendation=f"{vision.notes} Consider professional grading after a manual inspection.",
        selling_window="Sell now — demo market trend is stable.",
        pricing_source=pricing_source,
        identification_mode=identification_mode + "; grade calculated from uploaded image pixels",
        is_official_grade=False,
        processing_ms=max(1, int((time.perf_counter() - started) * 1000)),
        front_preview=front_preview,
        back_preview=back_preview,
        crop_status="Both card boundaries detected" if front_found and back_found else "Fallback crop used; retake on a plain dark background for best accuracy",
        card_candidates=candidate_profiles,
    )
    ASSESSMENT_HISTORY.append(assessment)
    return assessment
