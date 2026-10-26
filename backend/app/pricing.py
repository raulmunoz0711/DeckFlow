"""DeckFlow: free TCGdex market pricing, no JustTCG dependency.

The card's TCGdex ID is resolved through the local SQLite catalog, then its
TCGplayer USD market quote is fetched and cached for 12 hours. No graded-price
multipliers are fabricated. A missing quote is explicitly identified.
"""
from __future__ import annotations

import os
import re
import sqlite3
import time
from pathlib import Path
from urllib.parse import quote

import httpx

BASE = "https://api.tcgdex.net/v2"
CACHE_DB = Path(os.getenv("DECKFLOW_PRICE_DB", "/app/data/prices.sqlite3"))
TTL_SECONDS = 12 * 60 * 60

class CardSearchError(Exception):
    pass


def has_api_key() -> bool:
    """Kept for compatibility with legacy identification imports.

    TCGdex does not need a key; the existing offline catalog handles search.
    """
    return False


def _cache():
    CACHE_DB.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(CACHE_DB, timeout=10)
    db.execute("""CREATE TABLE IF NOT EXISTS market_prices (
        card_id TEXT PRIMARY KEY, usd REAL, variant TEXT,
        fetched_at INTEGER NOT NULL, source TEXT NOT NULL
    )""")
    return db


def _local_id(profile: dict) -> tuple[str | None, str | None]:
    """Prefer verified TCGdex IDs; otherwise exact-match name, set and number locally."""
    id_ = str(profile.get("tcgdex_id") or "")
    if id_:
        if ":" in id_:
            language, card_id = id_.split(":", 1)
        else:
            language, card_id = "en", id_
        if language in {"en", "ja"} and re.fullmatch(r"[a-zA-Z0-9_.-]{2,70}", card_id):
            return language, card_id
        return None, None
    try:
        from app.catalog import candidates
        query = f'{profile.get("card_name", "")} {profile.get("card_number", "")}'
        rows = candidates(query, limit=20)
        name = str(profile.get("card_name") or "").casefold().strip()
        set_name = str(profile.get("set_name") or "").casefold().strip()
        number = str(profile.get("card_number") or "").strip()
        matching = [r for r in rows if
                    r.get("card_name", "").casefold().strip() == name and
                    r.get("set_name", "").casefold().strip() == set_name and
                    str(r.get("card_number", "")).strip() == number]
        if len(matching) == 1:
            return _local_id(matching[0])
    except (ImportError, OSError, sqlite3.Error, ValueError):
        pass
    return None, None


def _choose_usd(pricing: dict) -> tuple[float | None, str]:
    data = pricing.get("tcgplayer") or {}
    if str(data.get("unit", "USD")).upper() != "USD":
        return None, ""
    # Prefer holofoil for a holo print; otherwise a deterministic non-foil fallback.
    for kind in ("holofoil", "holo", "normal", "reverse-holofoil", "reverse", "1st-edition", "unlimited"):
        variant = data.get(kind)
        if isinstance(variant, dict):
            price = variant.get("marketPrice")
            if isinstance(price, (int, float)) and price > 0:
                return round(float(price), 2), kind
    return None, ""


def _rough_graded_price(raw_price: float, estimated_grade: float) -> float:
    """Calculate a rough graded value from the raw price and estimated grade.

    This is a DeckFlow prototype estimate, not a verified PSA, BGS, or CGC
    sale price.
    """
    if raw_price <= 0:
        return 0.0

    grade = max(1.0, min(10.0, float(estimated_grade)))

    multipliers = {
        1: 0.35,
        2: 0.42,
        3: 0.50,
        4: 0.60,
        5: 0.75,
        6: 0.95,
        7: 1.20,
        8: 1.60,
        9: 2.40,
        10: 4.00,
    }

    lower_grade = int(grade)
    upper_grade = min(10, lower_grade + 1)
    fraction = grade - lower_grade

    multiplier = (
        multipliers[lower_grade]
        + (multipliers[upper_grade] - multipliers[lower_grade]) * fraction
    )

    return round(raw_price * multiplier, 2)


async def search_cards(query: str) -> list[dict]:
    """Compatibility fallback. Identification uses local catalog, not price API."""
    try:
        from app.catalog import candidates
        return candidates(query, limit=6)
    except (ImportError, OSError, sqlite3.Error):
        return []


async def search_card(query: str) -> dict | None:
    cards = await search_cards(query)
    return cards[0] if cards else None


async def get_prices(profile: dict, estimated_grade: float) -> tuple[float, float, str]:
    """Returns (raw USD market estimate, rough graded estimate, source)."""
    language, card_id = _local_id(profile)
    if not card_id:
        return 0.0, 0.0, "Select an exact TCGdex printing to retrieve a market price"
    key = f"{language}:{card_id}"
    try:
        with _cache() as db:
            cached = db.execute("SELECT usd,variant,fetched_at,source FROM market_prices WHERE card_id=?", (key,)).fetchone()
        if cached and int(time.time()) - cached[2] < TTL_SECONDS:
            if cached[0] is not None:
                raw = float(cached[0])
                graded = _rough_graded_price(raw, estimated_grade)
                return (
                    raw,
                    graded,
                    f"Cached TCGdex / TCGplayer USD {cached[1]} market quote "
                    "+ DeckFlow rough graded-value model (not a verified sale)",
                )
            return 0.0, 0.0, cached[3]
    except sqlite3.Error:
        cached = None
    try:
        url = f"{BASE}/{language}/cards/{quote(card_id, safe='')}"
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url, headers={"User-Agent": "DeckFlow-CPSC490/1.0"})
        if response.status_code == 429:
            raise CardSearchError("TCGdex temporarily rate-limited requests")
        response.raise_for_status()
        card = response.json()
        if not isinstance(card, dict) or card.get("id") != card_id:
            raise CardSearchError("TCGdex returned an unexpected card")
        price, variant = _choose_usd(card.get("pricing") or {})
        source = (
            f"TCGdex / TCGplayer USD {variant} market price "
            "+ DeckFlow rough graded-value model (not a verified sale)"
            if price is not None
            else "TCGdex has no USD market quote for this printing, "
                 "so a graded estimate cannot be calculated"
        )
        try:
            with _cache() as db:
                db.execute("INSERT OR REPLACE INTO market_prices VALUES (?,?,?,?,?)",
                           (key, price, variant, int(time.time()), source))
                db.commit()
        except sqlite3.Error:
            pass
        raw = price or 0.0
        graded = _rough_graded_price(raw, estimated_grade)
        return raw, graded, source
    except (httpx.HTTPError, ValueError, TypeError, CardSearchError) as e:
        if cached and cached[0] is not None:
            raw = float(cached[0])
            graded = _rough_graded_price(raw, estimated_grade)
            return (
                raw,
                graded,
                f"Older cached TCGdex USD price + DeckFlow rough graded-value "
                f"model (source temporarily unavailable; last fetched {cached[2]})",
            )
        return 0.0, 0.0, f"Market price unavailable: {type(e).__name__}; no fabricated values"
