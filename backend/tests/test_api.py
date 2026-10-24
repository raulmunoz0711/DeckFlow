import cv2
import numpy as np
from fastapi.testclient import TestClient

from app.main import ASSESSMENT_HISTORY, app

client = TestClient(app)


def card_image(color: tuple[int, int, int] = (80, 120, 180)) -> bytes:
    image = np.full((840, 600, 3), color, dtype=np.uint8)
    cv2.rectangle(image, (18, 18), (581, 821), (25, 45, 90), 18)
    cv2.rectangle(image, (48, 60), (551, 780), (210, 190, 120), 5)
    cv2.putText(image, "DECKFLOW TEST", (110, 420), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
    ok, encoded = cv2.imencode(".jpg", image)
    assert ok
    return encoded.tobytes()


def damaged_card_image() -> bytes:
    image = cv2.imdecode(np.frombuffer(card_image((70, 105, 165)), np.uint8), cv2.IMREAD_COLOR)
    # Simulated exposed paper/whitening, clipped corners, and diagonal creases.
    cv2.line(image, (0, 90), (0, 730), (245, 245, 245), 24)
    cv2.line(image, (599, 180), (599, 760), (245, 245, 245), 20)
    cv2.rectangle(image, (0, 0), (75, 75), (245, 245, 245), -1)
    cv2.rectangle(image, (525, 765), (599, 839), (245, 245, 245), -1)
    cv2.line(image, (90, 130), (520, 710), (250, 250, 250), 9)
    cv2.line(image, (130, 690), (500, 210), (15, 15, 15), 6)
    ok, encoded = cv2.imencode(".jpg", image)
    assert ok
    return encoded.tobytes()


def test_health() -> None:
    assert client.get("/api/health").json()["status"] == "ok"


def test_supported_cards() -> None:
    response = client.get("/api/cards")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_valid_assessment_and_history() -> None:
    ASSESSMENT_HISTORY.clear()
    files = {"front": ("front.jpg", card_image(), "image/jpeg"), "back": ("back.jpg", card_image((130, 80, 50)), "image/jpeg")}
    response = client.post("/api/assessments", files=files, data={"card_id": "pikachu-160"})
    assert response.status_code == 200
    assert response.json()["card_name"] == "Pikachu"
    assert response.json()["is_official_grade"] is False
    assert 1 <= response.json()["estimated_grade"] <= 10
    assert len(response.json()["defects"]) == 5
    assert len(client.get("/api/assessments").json()) == 1


def test_damaged_card_scores_below_clean_card() -> None:
    clean = {"front": ("front.jpg", card_image(), "image/jpeg"), "back": ("back.jpg", card_image(), "image/jpeg")}
    damaged = {"front": ("front.jpg", damaged_card_image(), "image/jpeg"), "back": ("back.jpg", damaged_card_image(), "image/jpeg")}
    clean_result = client.post("/api/assessments", files=clean, data={"card_id": "pikachu-160"}).json()
    damaged_result = client.post("/api/assessments", files=damaged, data={"card_id": "pikachu-160"}).json()
    assert damaged_result["estimated_grade"] <= clean_result["estimated_grade"] - 2.0
    assert any(item["severity"] in {"medium", "high"} for item in damaged_result["defects"])


def test_rejects_invalid_content_type() -> None:
    files = {"front": ("front.txt", b"x" * 200, "text/plain"), "back": ("back.jpg", b"x" * 200, "image/jpeg")}
    assert client.post("/api/assessments", files=files).status_code == 400


def test_rejects_unsupported_card() -> None:
    files = {"front": ("front.jpg", card_image(), "image/jpeg"), "back": ("back.jpg", card_image(), "image/jpeg")}
    assert client.post("/api/assessments", files=files, data={"card_id": "missing"}).status_code == 400


def test_rejects_non_image_bytes() -> None:
    files = {"front": ("front.jpg", b"x" * 300, "image/jpeg"), "back": ("back.jpg", b"x" * 300, "image/jpeg")}
    response = client.post("/api/assessments", files=files)
    assert response.status_code == 400
