import sqlite3
import pytest
from fastapi.testclient import TestClient
from app import catalog
from app.main import app

@pytest.fixture
def sample_catalog(monkeypatch, tmp_path):
    monkeypatch.setattr(catalog, "DB", tmp_path / "cards.sqlite3")
    with catalog.connect() as db:
        db.executemany("INSERT INTO cards VALUES (?,?,?,?,?,?,?,?)", [
          ("en:swsh12.5-018","en","Charizard V","018","018/160","swsh12.5","Crown Zenith", "https://example.com/c"),
          ("en:swsh9-017","en","Charizard V","017","017/186","swsh9","Brilliant Stars", "https://example.com/x"),
          ("en:bw7-33","en","Psyduck","33","33/153","bw7","Boundaries Crossed", "https://example.com/p"),
          ("en:base2-52","en","Exeggcute","52","52/64","base2","Jungle", "https://example.com/e"),
        ])
        db.commit()
    return catalog

@pytest.mark.parametrize("query,wanted", [
  ("Charizard V 018/159","en:swsh12.5-018"),
  ("Psyduck 33/149","en:bw7-33"),
  ("Exeggcute 52/64","en:base2-52"),
])
def test_printed_number_mismatch(sample_catalog, query, wanted):
    records=sample_catalog.candidates(query)
    assert len(records)==1 and records[0]["tcgdex_id"]==wanted

def test_no_wrong_species(sample_catalog):
    assert sample_catalog.candidates("Charizard VSTAR 018/159")==[]

def test_assessment_identity_and_price_flow(sample_catalog, monkeypatch):
    import cv2, numpy as np
    import app.main as service
    from types import SimpleNamespace

    image = np.full((840, 600, 3), 80, dtype=np.uint8)
    _, encoded = cv2.imencode('.jpg', image)
    img = encoded.tobytes()
    monkeypatch.setattr(service, 'analyze_card', lambda a,b: SimpleNamespace(
        grade=7.5, condition='Experimental', confidence=.45,
        centering='50/50', defects=[], notes='Unvalidated image analysis'))
    monkeypatch.setattr(service,'crop_preview', lambda b: ('data:image/jpeg;base64,AA==',True))
    async def fake_price(profile, grade):
        assert profile['tcgdex_id']=='en:swsh12.5-018'
        return 7.38,0.0,'Mocked TCGdex test USD market price'
    monkeypatch.setattr(service,'get_prices',fake_price)
    client=TestClient(app)
    response=client.post('/api/assessments',files={
        'front':('a.jpg',img,'image/jpeg'), 'back':('b.jpg',img,'image/jpeg')},
        data={'card_id':'charizard-ex-223','card_hint':'Charizard V 018/159', 'set_hint':'Crown Zenith'})
    assert response.status_code==200, response.text
    report=response.json()
    assert report['card_name']=='Charizard V'
    assert report['set_name']=='Crown Zenith'
    assert report['raw_market_price']==7.38
    assert report['card_candidates'][0]['tcgdex_id']=='en:swsh12.5-018'


def test_tcgplayer_usd_nested_holofoil():
    from app.pricing import _choose_usd, _local_id
    assert _choose_usd({"tcgplayer":{"unit":"USD","holofoil":{"marketPrice":7.38}}}) == (7.38,"holofoil")
    assert _local_id({"tcgdex_id":"en:swsh12.5-018"}) == ("en", "swsh12.5-018")


def test_candidate_selection_keeps_tcgdex_identity(sample_catalog, monkeypatch):
    import app.main as service
    async def fake_price(profile, grade):
        assert profile["tcgdex_id"] == "en:bw7-33"
        return 3.25, 0.0, "Mock TCGdex price"
    monkeypatch.setattr(service, "get_prices", fake_price)
    client=TestClient(app)
    body=client.post("/api/candidate-price",json={
        "card_name":"Psyduck", "set_name":"Boundaries Crossed",
        "card_number":"33/153", "variant":"Test", "tcgdex_id":"en:bw7-33",
        "estimated_grade":6.0,"condition":"Experimental"
    })
    assert body.status_code==200, body.text
    assert body.json()["raw_market_price"]==3.25
    assert body.json()["tcgdex_id"]=="en:bw7-33"


def test_synthetic_visible_damage_gets_lower_grade():
    # A regression guard for obvious, synthetic two-sided line damage.
    # This does not establish real-world grading accuracy.
    import cv2, numpy as np
    from app.grading import analyze_card
    from pathlib import Path
    def img(damaged):
        m=np.full((840,600,3),(80,120,180),dtype=np.uint8)
        cv2.rectangle(m,(18,18),(581,821),(25,45,90),18)
        cv2.rectangle(m,(48,60),(551,780),(210,190,120),5)
        cv2.putText(m,"DECKFLOW TEST",(110,420),cv2.FONT_HERSHEY_SIMPLEX,1.2,(255,255,255),3)
        if damaged:
            cv2.line(m,(90,130),(520,710),(250,250,250),9)
            cv2.line(m,(130,690),(500,210),(15,15,15),6)
        ok, b=cv2.imencode(".jpg",m)
        return b.tobytes()
    clean=img(False); damaged=img(True)
    assert analyze_card(damaged,damaged).grade < analyze_card(clean,clean).grade
