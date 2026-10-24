from __future__ import annotations

import re
from difflib import SequenceMatcher

import cv2
import numpy as np
import pytesseract

from app.grading import _extract_card
from app.pricing import CardSearchError, has_api_key, search_cards

NO_KEY_MODE = "Automatic identification is off: JUSTTCG_API_KEY is not set. Add it to .env and restart Docker, or type the card name/number"
OCR_NO_MATCH = "OCR could not confidently identify this card"


def _ocr_candidates(data: bytes) -> list[str]:
    image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        return []
    lines: list[str] = []
    card, _ = _extract_card(image)
    # Browser cameras can report orientation inconsistently. OCR every rotation
    # and favor card-name/collector-number lines when searching JustTCG.
    for rotated in (card, cv2.rotate(card, cv2.ROTATE_90_CLOCKWISE), cv2.rotate(card, cv2.ROTATE_180), cv2.rotate(card, cv2.ROTATE_90_COUNTERCLOCKWISE)):
        areas = [rotated[: int(rotated.shape[0] * .32)], rotated[int(rotated.shape[0] * .68):]]
        for area in areas:
            area = cv2.resize(area, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
            gray = cv2.cvtColor(area, cv2.COLOR_BGR2GRAY)
            text = pytesseract.image_to_string(gray, config="--psm 6")
            lines.extend(re.sub(r"[^A-Za-z0-9 /.'-]", " ", x).strip() for x in text.splitlines())
    return [x for x in lines if len(x) >= 3]


def _profile(card: dict) -> dict:
    card_set = card.get("set") or {}
    return {
        "card_name": card.get("name") or card.get("card_name") or "Unidentified Pokémon card",
        "set_name": card_set.get("name") if isinstance(card_set, dict) else (card_set or card.get("set_name") or "Unknown set"),
        "card_number": str(card.get("number") or card.get("card_number") or "Unknown number"),
        "variant": card.get("rarity") or card.get("variant") or "Pokémon TCG card",
        "justtcg_id": card.get("id") or card.get("slug"),
    }


def _norm_number(value: str) -> str:
    """'087/130' and '87/130' are the same collector number."""
    return re.sub(r"\b0+(\d)", r"\1", value.strip().lower())


def _match_basis(query: str, card: dict) -> str:
    """'number' only when a collector number in the query equals the card's; otherwise just 'name'."""
    found = re.search(r"\b\d{1,3}/\d{1,3}\b", query.lower())
    number = str(card.get("number") or card.get("card_number") or "")
    return "number" if found and _norm_number(found.group(0)) == _norm_number(number) else "name"


def _plausible_match(candidate: str, card: dict) -> bool:
    candidate_clean = re.sub(r"[^a-z0-9/]", " ", candidate.lower())
    name = str(card.get("name") or card.get("card_name") or "").lower()
    number = str(card.get("number") or card.get("card_number") or "").lower()
    number_match = re.search(r"\b\d{1,3}/\d{1,3}\b", candidate_clean)
    if number_match:
        return _norm_number(number_match.group(0)) == _norm_number(number)
    words = [word for word in candidate_clean.split() if len(word) >= 3 and not word.isdigit()]
    return bool(name) and any(word in name or SequenceMatcher(None, word, name).ratio() >= .72 for word in words)


async def identify_card_candidates(front_data: bytes, hint: str = "") -> tuple[list[dict], str]:
    matches: list[dict] = []
    seen: set[str] = set()
    async def add_results(query: str, require_similarity: bool) -> None:
        for card in await search_cards(query):
            if require_similarity and not _plausible_match(query, card):
                continue
            profile = {**_profile(card), "match_basis": _match_basis(query, card)}
            key = str(profile.get("justtcg_id") or f'{profile["card_name"]}:{profile["card_number"]}')
            if key not in seen:
                seen.add(key)
                matches.append(profile)
            if len(matches) >= 6:
                return

    # Without a key every JustTCG search returns nothing, so running ~5-9 s of OCR
    # first would only delay a guaranteed miss. Say why instead.
    if not has_api_key():
        return [], NO_KEY_MODE

    try:
        if hint.strip():
            await add_results(hint.strip(), False)
            if matches:
                return matches, "User-assisted JustTCG candidate search"

        lines = _ocr_candidates(front_data)
        # Try the cleanest short OCR lines first. Long rules text makes poor search input.
        candidates = sorted(lines, key=lambda x: (not bool(re.search(r"\d{1,3}/\d{1,3}", x)), abs(len(x) - 14)))
        for candidate in candidates[:8]:
            await add_results(candidate, True)
            if len(matches) >= 6:
                break
    except CardSearchError as exc:
        # Keep whatever was found before the failure; never crash the whole assessment.
        return matches, f"Automatic identification unavailable: {exc}"
    return matches, "AI-assisted OCR + JustTCG candidate search" if matches else OCR_NO_MATCH


async def identify_card(front_data: bytes, hint: str = "") -> tuple[dict | None, str]:
    matches, mode = await identify_card_candidates(front_data, hint)
    return (matches[0] if matches else None), mode
