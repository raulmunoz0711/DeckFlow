from __future__ import annotations

import hashlib
import time
from datetime import datetime, timezone
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.grading import analyze_card
from app.pricing import get_prices

app = FastAPI(title="DeckFlow Demo API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
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


ASSESSMENT_HISTORY: list[Assessment] = []


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


@app.get("/api/cards")
def supported_cards() -> list[dict]:
    return [{"id": key, **value} for key, value in CARD_PROFILES.items()]


@app.get("/api/assessments", response_model=list[Assessment])
def assessment_history() -> list[Assessment]:
    return list(reversed(ASSESSMENT_HISTORY[-20:]))


@app.post("/api/assessments", response_model=Assessment)
async def create_assessment(
    front: Annotated[UploadFile, File(description="Front image of a trading card")],
    back: Annotated[UploadFile, File(description="Back image of a trading card")],
    card_id: Annotated[str, Form()] = "charizard-ex-223",
) -> Assessment:
    started = time.perf_counter()
    front_bytes = await read_image(front, "front")
    back_bytes = await read_image(back, "back")
    profile = CARD_PROFILES.get(card_id)
    if not profile:
        raise HTTPException(status_code=400, detail="That card is not supported by this demonstration.")

    digest = hashlib.sha256(front_bytes + back_bytes).hexdigest()
    try:
        vision = analyze_card(front_bytes, back_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    grade = vision.grade
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
        identification_mode="Employee-confirmed card; grade calculated from uploaded image pixels",
        is_official_grade=False,
        processing_ms=max(1, int((time.perf_counter() - started) * 1000)),
    )
    ASSESSMENT_HISTORY.append(assessment)
    return assessment
