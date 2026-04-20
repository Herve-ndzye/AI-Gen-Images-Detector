"""
AI detection logic — predicts whether an image is AI-generated and
identifies suspicious regions using OpenCV heuristics.
"""

import cv2
import numpy as np
from typing import List, Dict, Any


# ──────────────────────────────────────────────────────────────────
#  AI Probability Prediction
# ──────────────────────────────────────────────────────────────────

def predict_ai_probability(image: np.ndarray) -> float:
    """
    Analyse an image and return a probability (0.0 – 1.0).
    Maximized ensemble including:
      1. ELA (Error Level Analysis)
      2. LBP (Local Binary Patterns) - Texture forensics
      3. CIE Lab - Color Consistency
      4. Grid / Harmonic detection
      5. Noise / Frequency heuristics
    """
    scores: list[float] = []

    scores.append(_ela_analysis(image))
    scores.append(_lbp_texture_analysis(image))
    scores.append(_color_consistency_analysis(image))
    scores.append(_grid_harmonic_analysis(image))
    scores.append(_noise_analysis(image))

    # Weighting: LBP and ELA are currently the strongest classical signals
    weights = [0.25, 0.30, 0.15, 0.20, 0.10]
    probability = float(np.clip(np.dot(scores, weights), 0.0, 1.0))
    return probability


def _lbp_texture_analysis(image: np.ndarray) -> float:
    """
    Local Binary Patterns (LBP).
    Detects if textures (skin, hair, clouds) are 'too perfect'.
    Digital generators lack the micro-imperfections of real light/lens physics.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Simple LBP approximation using bitwise comparison with neighbors
    h, w = gray.shape
    lbp = np.zeros((h-2, w-2), dtype=np.uint8)
    
    for i in range(1, h-1):
        for j in range(1, w-1):
            center = gray[i, j]
            code = 0
            code |= (gray[i-1, j-1] >= center) << 7
            code |= (gray[i-1, j] >= center) << 6
            code |= (gray[i-1, j+1] >= center) << 5
            code |= (gray[i, j+1] >= center) << 4
            code |= (gray[i+1, j+1] >= center) << 3
            code |= (gray[i+1, j] >= center) << 2
            code |= (gray[i+1, j-1] >= center) << 1
            code |= (gray[i, j-1] >= center) << 0
            lbp[i-1, j-1] = code

    # Analyze entropy of patterns
    hist, _ = np.histogram(lbp, bins=256, range=(0, 256), density=True)
    entropy = -np.sum(hist * np.log2(hist + 1e-7))

    # AI images often have lower LBP entropy (more predictable patterns)
    if entropy < 5.5:
        return 0.85
    elif entropy < 6.8:
        return 0.50
    return 0.15


def _color_consistency_analysis(image: np.ndarray) -> float:
    """
    Analyze color distribution in CIE Lab space.
    Real photos have sensors-specific 'crosstalk' between colors.
    AI images often have mathematically distinct separation.
    """
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2Lab)
    a_chan = lab[:, :, 1].astype(np.float32)
    b_chan = lab[:, :, 2].astype(np.float32)
    
    # Calculate correlation between red-green and blue-yellow channels
    correlation = np.corrcoef(a_chan.flatten(), b_chan.flatten())[0, 1]
    
    # AI often has 'too clean' separation (extreme correlation or zero correlation)
    abs_corr = abs(correlation)
    if abs_corr < 0.02 or abs_corr > 0.85:
        return 0.75
    return 0.30


def _ela_analysis(image: np.ndarray, quality: int = 90) -> float:
    """
    Error Level Analysis (ELA).
    Resaves the image at a specific quality and compares it to the original.
    AI images often show very uniform error levels, while real/edited images
    have distinct peaks in complex areas.
    """
    # 1. Compress to temporary buffer
    _, buffer = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    compressed = cv2.imdecode(buffer, cv2.IMREAD_COLOR)

    # 2. Calculate absolute difference
    diff = cv2.absdiff(image, compressed)
    
    # 3. Scale difference to make it visible/measurable
    diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    mean_diff = diff_gray.mean()

    # Empirical: AI images tend to have lower, more uniform ELA variance
    # whereas real photos have high variance due to lens noise/optics.
    if mean_diff < 1.0:
        return 0.90  # Extremely uniform (likely digital/AI)
    elif mean_diff < 2.5:
        return 0.65
    elif mean_diff > 8.0:
        return 0.20  # High entropy/noise (likely real camera)
    return 0.40


def _grid_harmonic_analysis(image: np.ndarray) -> float:
    """
    Detects "Checkerboard" artifacts.
    AI upsamplers leave periodic patterns. We look for spikes in the
    power spectrum at regular intervals.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    f = np.fft.fft2(gray.astype(np.float32))
    fshift = np.fft.fftshift(f)
    magnitude = np.abs(fshift)
    
    # Normalize
    magnitude = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
    
    # Look for unnatural "dots" in the frequency domain outside the center
    h, w = magnitude.shape
    center = (h // 2, w // 2)
    
    # Mask out the center (natural low frequencies)
    cv2.circle(magnitude, (center[1], center[0]), min(h, w) // 20, 0, -1)
    
    # If we find strong periodic spikes elsewhere, it's an AI fingerpint
    max_val = magnitude.max()
    if max_val > 200:
        return 0.85
    elif max_val > 150:
        return 0.60
    return 0.20


# ──────────────────────────────────────────────────────────────────
#  Heuristic helpers
# ──────────────────────────────────────────────────────────────────

def _noise_analysis(image: np.ndarray) -> float:
    """
    AI-generated images typically have unusually uniform / low noise.
    We estimate noise via the Laplacian variance on the grayscale image.
    Very low variance → likely AI → higher score.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    # Empirical thresholds (tuned on a sample of real vs AI images)
    if laplacian_var < 50:
        return 0.85          # very low noise → likely AI
    elif laplacian_var < 200:
        return 0.55
    elif laplacian_var < 800:
        return 0.30
    else:
        return 0.10          # high noise → likely real


def _frequency_analysis(image: np.ndarray) -> float:
    """
    AI images often have weaker high-frequency content.
    We compute the 2-D DFT and compare energy in high vs low frequencies.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    f = np.fft.fft2(gray.astype(np.float32))
    fshift = np.fft.fftshift(f)
    magnitude = np.log1p(np.abs(fshift))

    rows, cols = gray.shape
    crow, ccol = rows // 2, cols // 2

    # Low-frequency region (centre 10 %)
    r = min(rows, cols) // 10
    low_freq = magnitude[crow - r:crow + r, ccol - r:ccol + r].mean()
    high_freq = magnitude.mean()

    # Ratio: higher ratio → energy concentrated in low freq → AI-like
    if high_freq == 0:
        return 0.5
    ratio = low_freq / high_freq
    score = float(np.clip((ratio - 1.0) / 4.0, 0.0, 1.0))
    return score


def _colour_analysis(image: np.ndarray) -> float:
    """
    AI images frequently exhibit overly-smooth colour distributions.
    We measure the standard deviation of each HSV channel.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
    h_std = hsv[:, :, 0].std()
    s_std = hsv[:, :, 1].std()
    v_std = hsv[:, :, 2].std()

    combined_std = (h_std + s_std + v_std) / 3.0

    if combined_std < 20:
        return 0.80
    elif combined_std < 40:
        return 0.50
    elif combined_std < 60:
        return 0.30
    else:
        return 0.15


def _edge_coherence_analysis(image: np.ndarray) -> float:
    """
    AI images may have unnaturally smooth or uniform edges.
    We compute Canny edges and look at the density & uniformity.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    edge_density = edges.mean() / 255.0  # 0–1

    # Very low or very high density can be suspicious
    if edge_density < 0.02:
        return 0.75          # almost no edges → likely AI (smooth render)
    elif edge_density < 0.06:
        return 0.45
    elif edge_density < 0.15:
        return 0.20          # normal range for real photos
    else:
        return 0.35          # very busy edges (could be artefacts)


# ──────────────────────────────────────────────────────────────────
#  Suspicious Region Detection
# ──────────────────────────────────────────────────────────────────

def detect_suspicious_regions(image: np.ndarray) -> List[Dict[str, Any]]:
    """
    Detect regions that may indicate AI manipulation.

    MVP approach:
      1. Blur-map analysis  — regions with unusual blur
      2. Edge anomaly detection — patches where edge density deviates
         significantly from the image average
    Returns a list of ``{"x", "y", "width", "height", "reason"}`` dicts.
    """
    regions: List[Dict[str, Any]] = []
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    # --- Blur-based detection ---
    regions.extend(_detect_blur_regions(gray, h, w))

    # --- Edge anomaly detection ---
    regions.extend(_detect_edge_anomaly_regions(gray, h, w))

    # Deduplicate overlapping boxes (simple: keep first N unique)
    return _deduplicate_regions(regions, max_regions=8)


def _detect_blur_regions(
    gray: np.ndarray, h: int, w: int, block: int = 64, threshold_factor: float = 0.4
) -> List[Dict[str, Any]]:
    """Slide a window and flag blocks whose Laplacian variance is much
    lower than the image average (i.e. anomalously blurry)."""
    overall_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    threshold = overall_var * threshold_factor
    results: List[Dict[str, Any]] = []

    for y in range(0, h - block, block):
        for x in range(0, w - block, block):
            patch = gray[y:y + block, x:x + block]
            patch_var = cv2.Laplacian(patch, cv2.CV_64F).var()
            if patch_var < threshold and overall_var > 10:
                results.append({
                    "x": int(x),
                    "y": int(y),
                    "width": block,
                    "height": block,
                    "reason": "Anomalously blurred region",
                })
    return results


def _detect_edge_anomaly_regions(
    gray: np.ndarray, h: int, w: int, block: int = 64, z_threshold: float = 2.0
) -> List[Dict[str, Any]]:
    """Flag blocks where Canny edge density is statistically unusual."""
    edges = cv2.Canny(gray, 50, 150)
    overall_density = edges.mean()
    overall_std = edges.std()

    if overall_std == 0:
        return []

    results: List[Dict[str, Any]] = []
    for y in range(0, h - block, block):
        for x in range(0, w - block, block):
            patch = edges[y:y + block, x:x + block]
            density = patch.mean()
            z = abs(density - overall_density) / overall_std
            if z > z_threshold:
                label = (
                    "Unusually smooth region (possible AI artefact)"
                    if density < overall_density
                    else "Abnormally busy edges (possible artefact)"
                )
                results.append({
                    "x": int(x),
                    "y": int(y),
                    "width": block,
                    "height": block,
                    "reason": label,
                })
    return results


def _deduplicate_regions(
    regions: List[Dict[str, Any]], max_regions: int = 8
) -> List[Dict[str, Any]]:
    """Keep only distinct, non-overlapping regions up to *max_regions*."""
    if not regions:
        return []

    seen: set[tuple[int, int]] = set()
    unique: List[Dict[str, Any]] = []
    for r in regions:
        key = (r["x"], r["y"])
        if key not in seen:
            seen.add(key)
            unique.append(r)
        if len(unique) >= max_regions:
            break
    return unique
