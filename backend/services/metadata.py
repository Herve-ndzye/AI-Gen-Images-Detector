"""
Metadata extraction — reads EXIF / XMP data from image bytes.
"""

import io
from typing import Dict, Any, Optional

# PIL is used only for metadata extraction (not image processing)
from PIL import Image as PILImage
from PIL.ExifTags import TAGS


def extract_metadata(raw_bytes: bytes) -> Dict[str, Any]:
    """
    Extract metadata from raw image bytes.

    Returns a dict with at least:
        has_metadata : bool
        camera       : str | None
        software     : str | None
        timestamp    : str | None
        gps          : bool
        details      : dict   (all EXIF key-value pairs found)
    """
    result: Dict[str, Any] = {
        "has_metadata": False,
        "camera": None,
        "software": None,
        "timestamp": None,
        "gps": False,
        "details": {},
    }

    try:
        img = PILImage.open(io.BytesIO(raw_bytes))
        exif_data = img._getexif()  # noqa: SLF001

        if exif_data is None:
            return result

        decoded: Dict[str, Any] = {}
        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, str(tag_id))
            # Convert bytes to strings for JSON serialisation
            if isinstance(value, bytes):
                try:
                    value = value.decode("utf-8", errors="replace")
                except Exception:
                    value = str(value)
            decoded[tag_name] = value

        result["has_metadata"] = bool(decoded)
        result["details"] = _sanitise_for_json(decoded)

        # Camera info
        result["camera"] = (
            decoded.get("Model")
            or decoded.get("Make")
            or None
        )

        # Software
        result["software"] = decoded.get("Software")

        # Timestamp
        result["timestamp"] = (
            decoded.get("DateTimeOriginal")
            or decoded.get("DateTime")
            or None
        )

        # GPS presence
        result["gps"] = "GPSInfo" in decoded

    except Exception:
        # If metadata extraction fails, we just treat it as "no metadata"
        pass

    return result


def _sanitise_for_json(data: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure every value in *data* is JSON-serialisable."""
    clean: Dict[str, Any] = {}
    for k, v in data.items():
        if isinstance(v, (str, int, float, bool, type(None))):
            clean[k] = v
        elif isinstance(v, bytes):
            clean[k] = v.decode("utf-8", errors="replace")
        elif isinstance(v, dict):
            clean[k] = _sanitise_for_json(v)
        elif isinstance(v, (list, tuple)):
            clean[k] = [str(i) for i in v]
        else:
            clean[k] = str(v)
    return clean
