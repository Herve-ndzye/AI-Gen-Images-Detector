"""
Image utility helpers — decoding, validation, resizing.
"""

import cv2
import numpy as np
from typing import Optional


# Maximum dimension (width or height) for analysis — larger images are
# down-scaled to keep processing under 3-5 seconds.
MAX_ANALYSIS_DIM = 1024


def read_image_from_upload(raw_bytes: bytes) -> Optional[np.ndarray]:
    """
    Decode raw bytes into a BGR ``numpy`` array (OpenCV format).

    Returns ``None`` if decoding fails.
    """
    arr = np.frombuffer(raw_bytes, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    if image is None:
        return None

    # Down-scale if needed to guarantee fast analysis
    image = resize_for_analysis(image)
    return image


def validate_image_file(raw_bytes: bytes) -> bool:
    """Return ``True`` if *raw_bytes* can be decoded as a valid image."""
    arr = np.frombuffer(raw_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return img is not None


def resize_for_analysis(
    image: np.ndarray, max_dim: int = MAX_ANALYSIS_DIM
) -> np.ndarray:
    """
    Proportionally resize *image* so its largest dimension does not
    exceed *max_dim*.  Returns the original if no resize is needed.
    """
    h, w = image.shape[:2]
    if max(h, w) <= max_dim:
        return image

    scale = max_dim / max(h, w)
    new_w = int(w * scale)
    new_h = int(h * scale)
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
