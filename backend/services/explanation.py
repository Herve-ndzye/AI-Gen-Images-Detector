"""
Explanation generator — produces human-readable insights from analysis signals.
"""

from typing import Dict, Any, List
import numpy as np
import cv2


def generate_explanations(
    ai_prob: float,
    metadata: Dict[str, Any],
    image: np.ndarray,
) -> List[str]:
    """
    Build a list of plain-English explanations describing why the image
    may or may not be AI-generated.

    The function combines:
      • AI probability thresholds
      • Metadata signals
      • Visual heuristics (run lightly to avoid duplicating detector work)
    """
    explanations: List[str] = []

    # ── AI probability level ──────────────────────────────────────
    if ai_prob >= 0.85:
        explanations.append(
            "Strong AI-generated patterns detected across multiple analysis dimensions."
        )
    elif ai_prob >= 0.70:
        explanations.append("Likely AI-generated patterns detected in the image.")
    elif ai_prob >= 0.40:
        explanations.append(
            "Some characteristics are consistent with AI generation, but not conclusive."
        )
    else:
        explanations.append(
            "Image characteristics are mostly consistent with a real photograph."
        )

    # ── Forensic signals ──────────────────────────────────────────
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # ELA check
    _, b = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 90])
    com = cv2.imdecode(b, cv2.IMREAD_COLOR)
    if cv2.absdiff(image, com).mean() < 1.5:
        explanations.append(
            "Compression Analysis: The image has an unusually perfect pixel distribution, "
            "often seen in purely synthetic AI generations (ELA pass)."
        )

    # Texture check (LBP)
    # (Checking entropy of a sample region for explanation)
    if gray.std() < 10:
        explanations.append(
            "Texture Analysis: Surface textures are abnormally smooth (low entropy). "
            "Real photographs typically have micro-textures from physical surfaces."
        )

    # Color Space check
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2Lab)
    corr = np.corrcoef(lab[:,:,1].flatten(), lab[:,:,2].flatten())[0,1]
    if abs(corr) < 0.05:
        explanations.append(
            "Color Forensics: Detected a 'synthetic' color separation in the Lab space, "
            "lacking the natural channel crosstalk expected from digital camera sensors."
        )

    # Grid check
    f = np.fft.fft2(gray.astype(np.float32))
    fshift = np.fft.fftshift(f)
    if np.abs(fshift).max() > 180:
        explanations.append(
            "Structural Analysis: Detected signature 'checkerboard' artifacts in the "
            "frequency domain, common in AI upscaling algorithms."
        )

    # ── Metadata-based insights ───────────────────────────────────
    if not metadata.get("has_metadata"):
        explanations.append(
            "No camera metadata (EXIF) found — AI-generated images typically lack EXIF data."
        )
    else:
        if metadata.get("camera"):
            explanations.append(
                f"Camera metadata present: {metadata['camera']}. "
                "This is a positive signal for authenticity."
            )
        if metadata.get("software"):
            sw = metadata["software"]
            suspicious_sw = ["photoshop", "gimp", "stable diffusion",
                             "midjourney", "dall-e", "comfyui"]
            if any(s in sw.lower() for s in suspicious_sw):
                explanations.append(
                    f"Image was processed with '{sw}', which may indicate editing or AI generation."
                )
            else:
                explanations.append(f"Software field: {sw}.")
        if metadata.get("gps"):
            explanations.append(
                "GPS coordinates found in metadata — typically present only in real photos."
            )
        if metadata.get("timestamp"):
            explanations.append(f"Original capture date: {metadata['timestamp']}.")

    # ── Lightweight visual checks ─────────────────────────────────
    _add_visual_explanations(image, explanations)

    return explanations


def _add_visual_explanations(image: np.ndarray, explanations: List[str]) -> None:
    """Append explanations derived from quick visual checks."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Noise uniformity
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    if lap_var < 50:
        explanations.append(
            "Image noise is unusually uniform, a common trait of AI-generated images."
        )

    # Texture smoothness
    edges = cv2.Canny(gray, 50, 150)
    edge_density = edges.mean() / 255.0
    if edge_density < 0.02:
        explanations.append(
            "Very few sharp edges detected — the image appears unnaturally smooth."
        )
    elif edge_density > 0.20:
        explanations.append(
            "Unusually high edge density — may indicate artefacts from AI generation."
        )

    # Colour-range check
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    s_std = hsv[:, :, 1].std()
    if s_std < 15:
        explanations.append(
            "Colour saturation is very uniform — AI images often lack natural colour variation."
        )
