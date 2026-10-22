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
