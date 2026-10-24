"""Strict TCGdex SQLite matching. Never confuse 018/159 with 018/160."""
from __future__ import annotations
import os,re,sqlite3
from pathlib import Path
from difflib import SequenceMatcher
DB=Path(os.getenv('DECKFLOW_CATALOG_DB','/app/data/pokemon_cards.sqlite3'))
def connect():
 DB.parent.mkdir(parents=True,exist_ok=True)
 db=sqlite3.connect(DB,timeout=15)
 db.execute('''CREATE TABLE IF NOT EXISTS cards (id TEXT PRIMARY KEY,language TEXT NOT NULL,name TEXT NOT NULL,local_id TEXT NOT NULL,card_number TEXT NOT NULL,set_id TEXT,set_name TEXT,image_url TEXT)''')
 db.execute('CREATE INDEX IF NOT EXISTS cards_local ON cards(local_id)')
 db.execute('CREATE INDEX IF NOT EXISTS cards_name ON cards(name COLLATE NOCASE)')
 return db
def count():
 with connect() as db:return db.execute('SELECT COUNT(*) FROM cards').fetchone()[0]
def norm_number(s):
 m=re.fullmatch(r'\s*0*(\d+)\s*/\s*0*(\d+)\s*',str(s))
 return (int(m[1]),int(m[2])) if m else None
# DECKFLOW_NUMBER_FIX_V1: tolerate catalog set-total differences; confirm ambiguous printings.
def candidates(query: str, limit=6):
    query = query.strip()
    number_match = re.search(r'(?<!\d)(\d{1,4})\s*/\s*(\d{1,4})(?!\d)', query)
    wanted = norm_number(number_match.group(0)) if number_match else None
    # Remove the number from OCR/hint; avoid matching V with VSTAR.
    name = re.sub(r'\d{1,4}\s*/\s*\d{1,4}', ' ', query).strip().lower()
    name = re.sub(r'[^a-z0-9 ]', ' ', name)
    name = ' '.join(name.split())
    if not name or len(name) < 3:
        return []
    with connect() as db:
        db.row_factory = sqlite3.Row
        # The name filter prevents a huge number-only match across different sets.
        rows = db.execute(
            'SELECT * FROM cards WHERE name LIKE ? COLLATE NOCASE LIMIT 3000',
            ('%' + name + '%',),
        ).fetchall()
    ranked = []
    for row in rows:
        card_name = ' '.join(re.sub(r'[^a-z0-9 ]', ' ', row['name'].lower()).split())
        # Exact name, or close OCR spelling. Do not accept Charizard VSTAR for Charizard V.
        if card_name != name and SequenceMatcher(None, name, card_name).ratio() < .92:
            continue
        stored_number = norm_number(row['card_number'])
        if wanted:
            if stored_number is None or stored_number[0] != wanted[0]:
                continue
            # Full match ranks first. Same numerator with different denominator
            # remains a candidate requiring employee confirmation.
            number_score = 100 if stored_number == wanted else 35
        else:
            number_score = 0
        score = number_score + (40 if card_name == name else 0)
        ranked.append((score, dict(row)))
    ranked.sort(key=lambda item: (-item[0], item[1]['set_name'] or '', item[1]['id']))
    return [
        {
            'card_name': row['name'],
            'set_name': row['set_name'] or 'Unknown set',
            'card_number': row['card_number'],
            'variant': 'TCGdex catalog candidate — confirm printing',
            'tcgdex_id': row['id'],
            'justtcg_id': None,
            'image_url': row['image_url'],
            'match_basis': 'exact_number' if wanted and norm_number(row['card_number']) == wanted else 'name_and_collector_prefix' if wanted else 'name',
        }
        for _, row in ranked[:limit]
    ]

