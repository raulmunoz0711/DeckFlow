from __future__ import annotations

import os
from typing import Any

import httpx

API = "https://api.justtcg.com/v2/cards"


class CardSearchError(Exception):
    """JustTCG could not be searched (bad key, rate limit, outage). The message is safe to show the employee."""


def has_api_key() -> bool:
    return bool(os.getenv("JUSTTCG_API_KEY", "").strip())


def _price(variant: dict[str, Any]) -> float | None:
    market = next((m for m in variant.get("markets", []) if m.get("region", "").upper() == "NA"), None)
    return float(market["price"]) if market and market.get("price") is not None else None


async def search_cards(query: str) -> list[dict[str, Any]]:
    """Search first; v2 does not permit graded=include on browse/search."""
    key = os.getenv("JUSTTCG_API_KEY", "").strip()
    if not key or not query.strip():
        return []
    params = {"q": query.strip(), "game": "pokemon", "regions": "NA", "limit": 10}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(API, params=params, headers={"x-api-key": key})
            response.raise_for_status()
            return response.json().get("data", [])
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        if status in (401, 403):
            raise CardSearchError("JustTCG rejected the API key (check JUSTTCG_API_KEY in .env)") from exc
        if status == 429:
            raise CardSearchError("JustTCG rate limit reached; wait a minute and scan again") from exc
        raise CardSearchError(f"JustTCG returned HTTP {status}") from exc
    except (httpx.HTTPError, ValueError) as exc:
        raise CardSearchError("JustTCG could not be reached") from exc


async def search_card(query: str) -> dict[str, Any] | None:
    cards = await search_cards(query)
    return cards[0] if cards else None


async def get_prices(profile: dict, estimated_grade: float) -> tuple[float, float, str]:
    fallback_raw = float(profile.get("raw_market_price", 0))
    # A cached graded price must not appear as the same value for every grade.
    # This conservative model is only used when JustTCG has no priced PSA variant.
    grade_multiplier = max(.35, .45 + (estimated_grade / 10) ** 3 * 2.55)
    fallback_graded = round(fallback_raw * grade_multiplier, 2)
    fallback = (fallback_raw, fallback_graded, "Cached raw price + grade-dependent modeled estimate")
    key = os.getenv("JUSTTCG_API_KEY", "").strip()
    if not key:
        return fallback
    try:
        found = None
        if profile.get("justtcg_id"):
            found = {"id": profile["justtcg_id"]}
        else:
            found = await search_card(f'{profile["card_name"]} {profile.get("card_number", "")}')
        if not found:
            return fallback[0], fallback[1], "JustTCG returned no card match; cached prices shown"
        card_id = found.get("id") or found.get("slug")
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(API, params={"card_id": card_id, "regions": "NA", "graded": "include"}, headers={"x-api-key": key})
            response.raise_for_status()
            cards = response.json().get("data", [])
        card = cards[0] if cards else found
    except (httpx.HTTPError, CardSearchError, ValueError, TypeError, KeyError):
        return fallback[0], fallback[1], "JustTCG unavailable; cached demonstration prices shown"

    condition_rank = {"Mint": 0, "Near Mint": 0, "Excellent": 1, "Lightly Played": 1, "Moderately/Heavily Played": 3}
    api_rank = {"Near Mint": 0, "Lightly Played": 1, "Moderately Played": 2, "Heavily Played": 3, "Damaged": 4}
    target = condition_rank.get(profile.get("condition", "Near Mint"), 0)
    raw_options: list[tuple[int, float]] = []
    graded_options: list[tuple[float, float]] = []
    for variant in card.get("variants", []):
        price = _price(variant)
        if price is None:
            continue
        if variant.get("type") == "raw":
            raw_options.append((abs(api_rank.get(variant.get("condition"), 0) - target), price))
        elif variant.get("type") == "graded" and str(variant.get("grading", {}).get("company", "")).upper() == "PSA":
            grade = variant.get("grading", {}).get("grade")
            if grade is not None:
                graded_options.append((abs(float(grade) - estimated_grade), price))

    raw = min(raw_options, default=(0, fallback[0]))[1]
    graded = min(graded_options, default=(0, fallback[1]))[1]
    source = "Live JustTCG pricing"
    if not graded_options:
        source += "; grade-dependent modeled estimate (no matching priced PSA sale)"
    else:
        source += " (raw condition + nearest priced PSA grade)"
    return raw, graded, source

