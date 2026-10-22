from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class GradeResult:
    grade: float
    confidence: float
    centering: str
    defects: list[dict[str, str]]
    condition: str
    notes: str


def _decode(data: bytes) -> np.ndarray:
    image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if image is None or min(image.shape[:2]) < 180:
        raise ValueError("The image could not be read or is too small. Retake it in JPG, PNG, or WEBP format.")
    return image


def _order(points: np.ndarray) -> np.ndarray:
    points = points.reshape(4, 2).astype("float32")
    total = points.sum(axis=1)
    diff = np.diff(points, axis=1).ravel()
    return np.array([points[np.argmin(total)], points[np.argmin(diff)], points[np.argmax(total)], points[np.argmax(diff)]], dtype="float32")


def _extract_card(image: np.ndarray) -> tuple[np.ndarray, bool]:
    height, width = image.shape[:2]
    scale = min(1.0, 1100 / max(height, width))
    work = cv2.resize(image, None, fx=scale, fy=scale) if scale < 1 else image.copy()
    gray = cv2.cvtColor(work, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 45, 135)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8), iterations=2)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    image_area = work.shape[0] * work.shape[1]
    for contour in sorted(contours, key=cv2.contourArea, reverse=True)[:12]:
        if cv2.contourArea(contour) < image_area * 0.18:
            continue
        perimeter = cv2.arcLength(contour, True)
        polygon = cv2.approxPolyDP(contour, 0.025 * perimeter, True)
        if len(polygon) != 4 or not cv2.isContourConvex(polygon):
            continue
        source = _order(polygon)
        target = np.array([[0, 0], [599, 0], [599, 839], [0, 839]], dtype="float32")
        return cv2.warpPerspective(work, cv2.getPerspectiveTransform(source, target), (600, 840)), True

    # API sample images are already tightly cropped; camera images fall back to a centered card crop.
    target_ratio = 600 / 840
    current_ratio = width / height
    if current_ratio > target_ratio:
        crop_width = int(height * target_ratio)
        left = (width - crop_width) // 2
        crop = image[:, left:left + crop_width]
    else:
        crop_height = int(width / target_ratio)
        top = (height - crop_height) // 2
        crop = image[top:top + crop_height, :]
    return cv2.resize(crop, (600, 840)), False


def _centering(card: np.ndarray) -> tuple[float, float, float]:
    gray = cv2.cvtColor(card, cv2.COLOR_BGR2GRAY).astype(np.float32)
    x_energy = np.mean(np.abs(np.diff(gray, axis=1)), axis=0)
    y_energy = np.mean(np.abs(np.diff(gray, axis=0)), axis=1)
    width, height = card.shape[1], card.shape[0]

    left = int(np.argmax(x_energy[int(width * .035):int(width * .20)]) + width * .035)
    right_from_edge = width - int(np.argmax(x_energy[int(width * .80):int(width * .965)]) + width * .80)
    top = int(np.argmax(y_energy[int(height * .025):int(height * .16)]) + height * .025)
    bottom_from_edge = height - int(np.argmax(y_energy[int(height * .84):int(height * .975)]) + height * .84)

    horizontal = 100 * left / max(1, left + right_from_edge)
    vertical = 100 * top / max(1, top + bottom_from_edge)
    deviation = (abs(horizontal - 50) + abs(vertical - 50)) / 2
    return horizontal, vertical, deviation


def _condition(grade: float) -> str:
    if grade >= 9: return "Mint"
    if grade >= 8: return "Near Mint"
    if grade >= 6: return "Excellent"
    if grade >= 4: return "Lightly Played"
    return "Moderately/Heavily Played"


def analyze_card(front_data: bytes, back_data: bytes) -> GradeResult:
    front, front_found = _extract_card(_decode(front_data))
    back, back_found = _extract_card(_decode(back_data))
    hf, vf, df = _centering(front)
    hb, vb, db = _centering(back)

    front_gray = cv2.cvtColor(front, cv2.COLOR_BGR2GRAY)
    back_gray = cv2.cvtColor(back, cv2.COLOR_BGR2GRAY)
    sharpness = min(cv2.Laplacian(front_gray, cv2.CV_64F).var(), cv2.Laplacian(back_gray, cv2.CV_64F).var())
    glare = max(float(np.mean(front_gray > 248)), float(np.mean(back_gray > 248)))
    darkness = max(float(np.mean(front_gray < 18)), float(np.mean(back_gray < 18)))

    band = 14
    border = np.concatenate([
        back_gray[:band, :].ravel(), back_gray[-band:, :].ravel(),
        back_gray[:, :band].ravel(), back_gray[:, -band:].ravel(),
    ])
    whitening = float(np.mean(border > 205))

    patch = 55
    corners = [back_gray[:patch, :patch], back_gray[:patch, -patch:], back_gray[-patch:, :patch], back_gray[-patch:, -patch:]]
    corner_means = np.array([float(np.mean(c)) for c in corners])
    corner_difference = float(np.std(corner_means))

    centering_penalty = max(0.0, ((df + db) / 2 - 3.0) * .10)
    edge_penalty = min(2.3, whitening * 7.0)
    corner_penalty = min(1.6, max(0.0, corner_difference - 5.0) * .045)
    surface_penalty = min(1.5, glare * 10.0 + darkness * 4.0)
    focus_penalty = min(1.8, max(0.0, 110.0 - sharpness) / 65.0)
    grade = round(max(1.0, min(10.0, 10.0 - centering_penalty - edge_penalty - corner_penalty - surface_penalty - focus_penalty)) * 2) / 2

    centering_severity = "none" if (df + db) / 2 < 5 else "low" if (df + db) / 2 < 10 else "medium"
    edge_severity = "none" if whitening < .025 else "low" if whitening < .09 else "medium"
    corner_severity = "none" if corner_difference < 8 else "low" if corner_difference < 18 else "medium"
    surface_severity = "none" if glare < .015 and darkness < .02 else "low" if glare < .06 else "medium"
    focus_severity = "none" if sharpness >= 110 else "low" if sharpness >= 55 else "medium"
    defects = [
        {"category": "Centering", "result": f"Front {hf:.0f}/{100-hf:.0f} horizontal; back {hb:.0f}/{100-hb:.0f}", "severity": centering_severity},
        {"category": "Corners", "result": f"Corner consistency difference: {corner_difference:.1f}", "severity": corner_severity},
        {"category": "Edges", "result": f"Possible whitening along {whitening * 100:.1f}% of the outer back edge", "severity": edge_severity},
        {"category": "Surface", "result": f"Glare {glare * 100:.1f}%; dark obstruction {darkness * 100:.1f}%", "severity": surface_severity},
        {"category": "Photo quality", "result": f"Focus score {sharpness:.0f}", "severity": focus_severity},
    ]
    quality = min(1.0, sharpness / 180.0) * (1 - min(.6, glare + darkness))
    confidence = max(.35, min(.92, .50 + quality * .28 + .07 * int(front_found) + .07 * int(back_found)))
    note = "Card boundaries detected on both images." if front_found and back_found else "One or both card boundaries used a centered fallback crop; retake against a plain dark background for better accuracy."
    return GradeResult(grade, round(confidence, 2), f"{hf:.0f}/{100-hf:.0f} front, {hb:.0f}/{100-hb:.0f} back", defects, _condition(grade), note)
