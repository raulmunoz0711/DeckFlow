from __future__ import annotations

import base64
import io
from dataclasses import dataclass

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageOps


@dataclass
class GradeResult:
    grade: float
    confidence: float
    centering: str
    defects: list[dict[str, str]]
    condition: str
    notes: str


def _damage_metrics(card: np.ndarray) -> tuple[float, float, float]:
    """Return edge whitening, corner damage, and surface-line anomaly ratios.

    These are deliberately conservative image heuristics for a classroom
    pre-grade. They work best with a tightly framed card on a dark background.
    """
    gray = cv2.cvtColor(card, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(card, cv2.COLOR_BGR2HSV)
    height, width = gray.shape

    # Compare the outer edge with the nearby inner edge. Damage on Pokemon card
    # backs commonly exposes bright, low-saturation paper along the blue border.
    edge = max(8, int(min(height, width) * .025))
    inner = edge * 3
    outer_mask = np.zeros_like(gray, dtype=bool)
    outer_mask[:edge, :] = True
    outer_mask[-edge:, :] = True
    outer_mask[:, :edge] = True
    outer_mask[:, -edge:] = True
    inner_mask = np.zeros_like(gray, dtype=bool)
    inner_mask[edge:inner, edge:-edge] = True
    inner_mask[-inner:-edge, edge:-edge] = True
    inner_mask[edge:-edge, edge:inner] = True
    inner_mask[edge:-edge, -inner:-edge] = True
    paper_like = (hsv[:, :, 1] < 75) & (hsv[:, :, 2] > 155)
    outer_white = float(np.mean(paper_like[outer_mask]))
    inner_white = float(np.mean(paper_like[inner_mask]))
    edge_whitening = max(0.0, outer_white - inner_white * .55)

    # A damaged corner is often much brighter or darker than the surrounding
    # border. Compare every corner with a nearby edge reference.
    patch = max(30, int(min(height, width) * .09))
    corners = [gray[:patch, :patch], gray[:patch, -patch:], gray[-patch:, :patch], gray[-patch:, -patch:]]
    refs = [
        gray[:patch, patch:patch * 2], gray[:patch, -patch * 2:-patch],
        gray[-patch:, patch:patch * 2], gray[-patch:, -patch * 2:-patch],
    ]
    corner_delta = np.array([abs(float(np.mean(c)) - float(np.mean(r))) for c, r in zip(corners, refs)])
    corner_damage = float(np.mean(np.clip((corner_delta - 8.0) / 55.0, 0.0, 1.0)))

    # Long, unusually straight high-contrast marks can indicate a crease or a
    # strong scratch. Ignore the printed border and only inspect the interior.
    interior = gray[inner:-inner, inner:-inner]
    edges = cv2.Canny(cv2.GaussianBlur(interior, (5, 5), 0), 80, 190)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=75,
                            minLineLength=int(min(interior.shape) * .22), maxLineGap=10)
    anomaly_length = 0.0
    if lines is not None:
        for line in lines[:40]:
            x1, y1, x2, y2 = line[0]
            length = float(np.hypot(x2 - x1, y2 - y1))
            angle = abs(np.degrees(np.arctan2(y2 - y1, x2 - x1))) % 90
            # Printed card layouts contain many horizontal/vertical rules; a
            # diagonal line is more suspicious as physical damage.
            if 12 < angle < 78:
                anomaly_length += length
    surface_anomaly = min(1.0, anomaly_length / (min(interior.shape) * 2.2))
    return edge_whitening, corner_damage, surface_anomaly


def _decode(data: bytes) -> np.ndarray:
    try:
        # Phone/webcam JPEGs commonly store rotation in EXIF. OpenCV ignores it.
        pil = ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")
        image = cv2.cvtColor(np.asarray(pil), cv2.COLOR_RGB2BGR)
    except Exception:
        image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if image is None or min(image.shape[:2]) < 180:
        raise ValueError("The image could not be read or is too small. Retake it in JPG, PNG, or WEBP format.")
    return image


def crop_preview(data: bytes) -> tuple[str, bool]:
    """Return a perspective-corrected card-only JPEG data URL."""
    card, found = _extract_card(_decode(data))
    ok, encoded = cv2.imencode(".jpg", card, [cv2.IMWRITE_JPEG_QUALITY, 92])
    if not ok:
        raise ValueError("The cropped card preview could not be created.")
    return "data:image/jpeg;base64," + base64.b64encode(encoded.tobytes()).decode("ascii"), found


def rotate_image_bytes(data: bytes, quarter_turns: int) -> bytes:
    image = _decode(data)
    turns = quarter_turns % 4
    if turns == 1:
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    elif turns == 2:
        image = cv2.rotate(image, cv2.ROTATE_180)
    elif turns == 3:
        image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    ok, encoded = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 95])
    if not ok:
        raise ValueError("The rotated card image could not be created.")
    return encoded.tobytes()


def _order(points: np.ndarray) -> np.ndarray:
    points = points.reshape(4, 2).astype("float32")
    total = points.sum(axis=1)
    diff = np.diff(points, axis=1).ravel()
    return np.array([points[np.argmin(total)], points[np.argmin(diff)], points[np.argmax(total)], points[np.argmax(diff)]], dtype="float32")


def _ocr_orientation_score(image: np.ndarray) -> float:
    """Higher when Tesseract sees readable upright words/numbers."""
    height, width = image.shape[:2]
    scale = min(1.0, 700 / max(height, width))
    work = cv2.resize(image, None, fx=scale, fy=scale) if scale < 1 else image
    gray = cv2.cvtColor(work, cv2.COLOR_BGR2GRAY)
    try:
        data = pytesseract.image_to_data(gray, config="--psm 11", output_type=pytesseract.Output.DICT)
        return sum(max(0.0, float(conf)) for text, conf in zip(data["text"], data["conf"]) if len(text.strip()) >= 2)
    except (ValueError, TypeError, pytesseract.TesseractError):
        return 0.0


def _upright_by_ocr(image: np.ndarray) -> np.ndarray:
    rotations = [
        image,
        cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE),
        cv2.rotate(image, cv2.ROTATE_180),
        cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE),
    ]
    return max(rotations, key=_ocr_orientation_score)


def _extract_card(image: np.ndarray) -> tuple[np.ndarray, bool]:
    height, width = image.shape[:2]
    scale = min(1.0, 1100 / max(height, width))
    work = cv2.resize(image, None, fx=scale, fy=scale) if scale < 1 else image.copy()
    gray = cv2.cvtColor(work, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 45, 135)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8), iterations=2)
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    image_area = work.shape[0] * work.shape[1]
    candidates: list[tuple[float, np.ndarray]] = []
    for contour in sorted(contours, key=cv2.contourArea, reverse=True)[:40]:
        area = cv2.contourArea(contour)
        # Phone photos often show a card occupying only 5-15% of the frame.
        if area < image_area * 0.015 or area > image_area * .92:
            continue
        perimeter = cv2.arcLength(contour, True)
        polygons = [cv2.approxPolyDP(contour, epsilon * perimeter, True) for epsilon in (.018, .025, .035, .05)]
        polygon = next((p for p in polygons if len(p) == 4 and cv2.isContourConvex(p)), None)
        if polygon is None:
            # Rounded card corners sometimes create more than four contour points.
            polygon = cv2.boxPoints(cv2.minAreaRect(contour)).reshape(4, 1, 2)
        source = _order(polygon)
        side_a = np.linalg.norm(source[1] - source[0])
        side_b = np.linalg.norm(source[2] - source[1])
        short, long = sorted((side_a, side_b))
        if long <= 0:
            continue
        ratio = short / long
        # Standard cards are about 0.714 wide/tall; allow perspective distortion.
        if not .54 <= ratio <= .84:
            continue
        rectangularity = min(1.0, area / max(1.0, side_a * side_b))
        score = area / image_area + rectangularity * .22 - abs(ratio - (600 / 840)) * .35
        candidates.append((score, source))

    if candidates:
        source = max(candidates, key=lambda item: item[0])[1]
        # Rotate landscape point ordering into portrait orientation when necessary.
        if np.linalg.norm(source[1] - source[0]) > np.linalg.norm(source[2] - source[1]):
            source = np.roll(source, -1, axis=0)
        target = np.array([[0, 0], [599, 0], [599, 839], [0, 839]], dtype="float32")
        warped = cv2.warpPerspective(work, cv2.getPerspectiveTransform(source, target), (600, 840))
        upside_down = cv2.rotate(warped, cv2.ROTATE_180)
        return max((warped, upside_down), key=_ocr_orientation_score), True

    # If edge detection is uncertain, use the same centered 2.5 x 3.5 region
    # displayed by the camera guide. This removes most of the room/person.
    target_ratio = 600 / 840
    guide_height = int(height * .82)
    guide_width = int(guide_height * target_ratio)
    if guide_width > width * .62:
        guide_width = int(width * .52)
        guide_height = int(guide_width / target_ratio)
    left = max(0, (width - guide_width) // 2)
    top = max(0, (height - guide_height) // 2)
    guided = image[top:top + guide_height, left:left + guide_width]
    height, width = guided.shape[:2]
    current_ratio = width / height
    if current_ratio > target_ratio:
        crop_width = int(height * target_ratio)
        left = (width - crop_width) // 2
        crop = guided[:, left:left + crop_width]
    else:
        crop_height = int(width / target_ratio)
        top = (height - crop_height) // 2
        crop = guided[top:top + crop_height, :]
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

    front_edge, front_corner, front_surface = _damage_metrics(front)
    back_edge, back_corner, back_surface = _damage_metrics(back)
    whitening = max(front_edge, back_edge)
    corner_damage = max(front_corner, back_corner)
    surface_anomaly = max(front_surface, back_surface)

    centering_penalty = max(0.0, ((df + db) / 2 - 3.0) * .10)
    edge_penalty = min(3.0, whitening * 9.0)
    corner_penalty = min(2.0, corner_damage * 3.2)
    surface_penalty = min(2.4, glare * 8.0 + darkness * 3.0 + surface_anomaly * 2.2)
    focus_penalty = min(1.8, max(0.0, 110.0 - sharpness) / 65.0)
    grade = round(max(1.0, min(10.0, 10.0 - centering_penalty - edge_penalty - corner_penalty - surface_penalty - focus_penalty)) * 2) / 2

    centering_severity = "none" if (df + db) / 2 < 5 else "low" if (df + db) / 2 < 10 else "medium"
    edge_severity = "none" if whitening < .025 else "low" if whitening < .09 else "medium"
    corner_severity = "none" if corner_damage < .08 else "low" if corner_damage < .25 else "medium" if corner_damage < .5 else "high"
    surface_severity = "none" if glare < .015 and darkness < .02 and surface_anomaly < .12 else "low" if surface_anomaly < .3 and glare < .06 else "medium" if surface_anomaly < .65 else "high"
    focus_severity = "none" if sharpness >= 110 else "low" if sharpness >= 55 else "medium"
    defects = [
        {"category": "Centering", "result": f"Front {hf:.0f}/{100-hf:.0f} horizontal; back {hb:.0f}/{100-hb:.0f}", "severity": centering_severity},
        {"category": "Corners", "result": f"Possible corner damage score: {corner_damage * 100:.0f}%", "severity": corner_severity},
        {"category": "Edges", "result": f"Possible whitening score: {whitening * 100:.1f}%", "severity": edge_severity},
        {"category": "Surface", "result": f"Possible crease/scratch score: {surface_anomaly * 100:.0f}%; glare {glare * 100:.1f}%", "severity": surface_severity},
        {"category": "Photo quality", "result": f"Focus score {sharpness:.0f}", "severity": focus_severity},
    ]
    quality = min(1.0, sharpness / 180.0) * (1 - min(.6, glare + darkness))
    confidence = max(.35, min(.92, .50 + quality * .28 + .07 * int(front_found) + .07 * int(back_found)))
    note = "Card boundaries detected on both images." if front_found and back_found else "One or both card boundaries used a centered fallback crop; retake against a plain dark background for better accuracy."
    return GradeResult(grade, round(confidence, 2), f"{hf:.0f}/{100-hf:.0f} front, {hb:.0f}/{100-hb:.0f} back", defects, _condition(grade), note)
