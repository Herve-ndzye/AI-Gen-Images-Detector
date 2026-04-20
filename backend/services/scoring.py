"""
Trust score computation — combines AI detection probability with metadata
signals into a single 0–1 trust score.
"""

from typing import Dict, Any


def compute_trust_score(ai_prob: float, metadata: Dict[str, Any]) -> float:
    """
    Compute the overall trust score for an image.

    Formula:
        trust_score = (1 - ai_prob) * 0.6 + metadata_score * 0.4

    Where *metadata_score* is refined beyond a simple binary:
      • +0.30  if any EXIF metadata exists
      • +0.20  if a camera model is present
      • +0.20  if a timestamp is present
      • +0.15  if GPS data is present
      • +0.15  if software is benign (i.e. NOT known AI tool)

    The metadata_score is capped at 1.0.

    Returns:
        float between 0 and 1 — higher means more trustworthy.
    """
    metadata_score = _compute_metadata_score(metadata)
    trust = (1 - ai_prob) * 0.6 + metadata_score * 0.4
    return max(0.0, min(1.0, trust))


def _compute_metadata_score(metadata: Dict[str, Any]) -> float:
    """Break metadata presence into a weighted sub-score."""
    score = 0.0

    if metadata.get("has_metadata"):
        score += 0.30

    if metadata.get("camera"):
        score += 0.20

    if metadata.get("timestamp"):
        score += 0.20

    if metadata.get("gps"):
        score += 0.15

    software = metadata.get("software") or ""
    suspicious_sw = ["stable diffusion", "midjourney", "dall-e", "comfyui"]
    if software and not any(s in software.lower() for s in suspicious_sw):
        score += 0.15

    return min(score, 1.0)
