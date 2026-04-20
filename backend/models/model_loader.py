"""
Model loader — placeholder for loading a pretrained AI-image-detection model.

When a real model is ready, implement ``load_model()`` to return the model
object and ``predict(model, image)`` to run inference.
"""

from typing import Any, Optional
import numpy as np

_model_cache: Optional[Any] = None


def load_model(model_path: Optional[str] = None) -> Any:
    """
    Load and cache a pretrained AI-image detection model.

    For the MVP this returns a sentinel object.  Replace the body
    with real model-loading code (e.g. ONNX, PyTorch, TensorFlow).
    """
    global _model_cache

    if _model_cache is not None:
        return _model_cache

    # ── Placeholder ────────────────────────────────────────────────
    # Replace this block with, e.g.:
    #   import onnxruntime as ort
    #   session = ort.InferenceSession(model_path or "weights/detector.onnx")
    #   _model_cache = session
    #   return session
    _model_cache = {"type": "placeholder", "version": "1.0.0"}
    return _model_cache


def predict(model: Any, image: np.ndarray) -> float:
    """
    Run inference on *image* using *model*.

    Returns a float 0-1 representing the probability that the image
    is AI-generated.

    Currently a stub — delegates to heuristic logic.
    """
    # When a real model is integrated:
    #   preprocessed = preprocess(image)
    #   output = model.run(None, {"input": preprocessed})
    #   return float(output[0][0])
    from services.detector import predict_ai_probability
    return predict_ai_probability(image)
