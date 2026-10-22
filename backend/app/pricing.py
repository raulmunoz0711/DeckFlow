from __future__ import annotations

import os
from typing import Any

import httpx


def _market_price(variant: dict[str, Any]) -> float | None:
    for market in variant.get("markets", []):
        if market.get("region") == "NA" and market.get("currency") == "USD" and market.get("price") is not None:
            return float(market["price"])
    return None


async def get_prices(profile: dict, estimated_grade: float) -> tuple[float, float, str]:
    fallback = (float(profile["raw_market_price"]), float(profile["graded_market_price"]), "Cached demonstration market dataset")
    api_key = os.getenv("JUSTTCG_API_KEY", "").strip()
    if not api_key:
        return fallback

    params = {"q": f'{profile["card_name"]} {profile["card_number"]}', "game": "pokemon", "regions": "NA", "graded": "include", "grading_company": "PSA", "limit": 20}
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get("https://api.justtcg.com/v2/cards", params=params, headers={"x-api-key": api_key})
            response.raise_for_status()
            cards = response.json().get("data", [])
    except (httpx.HTTPError, ValueError, TypeError):
        return fallback[0], fallback[1], "JustTCG unavailable; cached demonstration prices shown"

    wanted_set = profile["set_name"].casefold()
    wanted_number = profile["card_number"].split("/")[0].lstrip("0")
    match = next((card for card in cards if str(card.get("set", {}).get("name", "")).casefold() == wanted_set and str(card.get("number", "")).split("/")[0].lstrip("0") == wanted_number), None)
    if not match:
        return fallback[0], fallback[1], "JustTCG returned no exact card match; cached prices shown"

    condition_rank = {"Mint": 0, "Near Mint": 0, "Excellent": 1, "Lightly Played": 1, "Moderately/Heavily Played": 3}
    api_rank = {"Near Mint": 0, "Lightly Played": 1, "Moderately Played": 2, "Heavily Played": 3, "Damaged": 4}
    target_rank = condition_rank.get(profile.get("condition", "Near Mint"), 0)
    raw_options: list[tuple[int, float]] = []
    graded_options: list[tuple[float, float]] = []
    for variant in match.get("variants", []):
        price = _market_price(variant)
        if price is None:
            continue
        if variant.get("type") == "raw":
            raw_options.append((abs(api_rank.get(variant.get("condition"), 0) - target_rank), price))
        elif variant.get("type") == "graded" and variant.get("grading", {}).get("company") == "PSA":
            value = variant.get("grading", {}).get("grade")
            if value is not None:
                graded_options.append((abs(float(value) - estimated_grade), price))

    raw = min(raw_options, default=(0, fallback[0]))[1]
    graded = min(graded_options, default=(0, fallback[1]))[1]
    return raw, graded, "Live JustTCG North America pricing (raw condition + nearest PSA grade)"
