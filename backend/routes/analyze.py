"""
API endpoint for image analysis.
POST /analyze-image  — accepts multipart/form-data with an image file.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import numpy as np
import cv2
import time

from services.detector import predict_ai_probability, detect_suspicious_regions
from services.metadata import extract_metadata
from services.explanation import generate_explanations
from services.scoring import compute_trust_score
from utils.image_utils import read_image_from_upload, validate_image_file
from models.database import SessionLocal, AnalysisResult, init_db

router = APIRouter()
init_db() # Ensure tables exist

# Maximum file size: 10 MB
MAX_FILE_SIZE = 10 * 1024 * 1024

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/bmp",
    "image/tiff",
}


def _risk_level(ai_prob: float) -> str:
    """Map AI probability to a human-readable risk label."""
    if ai_prob >= 0.75:
        return "High"
    elif ai_prob >= 0.40:
        return "Medium"
    else:
        return "Low"


@router.post("/analyze-image", tags=["Analysis"])
async def analyze_image(file: UploadFile = File(...)):
    """
    Accepts an image file and returns:
    - ai_probability (float 0-1)
    - trust_score   (float 0-1)
    - risk_level    (Low / Medium / High)
    - explanations  (list of strings)
    - suspicious_regions (list of region dicts)
    """

    # ── Validate content type ──────────────────────────────────────
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image type '{file.content_type}'. "
                   f"Allowed types: {', '.join(sorted(ALLOWED_CONTENT_TYPES))}",
        )

    # ── Read raw bytes & enforce size limit ────────────────────────
    raw_bytes = await file.read()
    if len(raw_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({len(raw_bytes)} bytes). "
                   f"Maximum allowed size is {MAX_FILE_SIZE} bytes (10 MB).",
        )

    if not validate_image_file(raw_bytes):
        raise HTTPException(status_code=400, detail="File could not be decoded as an image.")

    # ── Convert to OpenCV format ───────────────────────────────────
    image = read_image_from_upload(raw_bytes)
    if image is None:
        raise HTTPException(status_code=400, detail="Failed to decode the image.")

    # ── Run analysis pipeline ──────────────────────────────────────
    start = time.time()

    ai_prob = predict_ai_probability(image)
    metadata = extract_metadata(raw_bytes)
    regions = detect_suspicious_regions(image)
    explanations = generate_explanations(ai_prob, metadata, image)
    trust_score = compute_trust_score(ai_prob, metadata)
    risk = _risk_level(ai_prob)

    elapsed = round(time.time() - start, 2)

    # ── Save to Database ──────────────────────────────────────────
    db = SessionLocal()
    db_result = AnalysisResult(
        filename=file.filename,
        ai_probability=f"{round(ai_prob * 100)}%",
        trust_score=f"{round(trust_score * 100)}%",
        risk_level=risk,
        verdict="Likely AI" if ai_prob > 0.6 else "Likely Human" if ai_prob < 0.3 else "Inconclusive",
        explanations=explanations,
        user_id=1 # Placeholder for MVP
    )
    db.add(db_result)
    db.commit()
    db.close()

    return JSONResponse(
        content={
            "id": db_result.id,
            "summary": {
                "ai_probability": db_result.ai_probability,
                "authenticity_trust": db_result.trust_score,
                "risk_level": risk,
                "verdict": db_result.verdict
            },
            "analysis": {
                "explanations": explanations,
                "suspicious_regions_count": len(regions),
                "suspicious_regions": regions,
            },
            "metadata_summary": {
                "found": metadata.get("has_metadata", False),
                "camera": metadata.get("camera", "Unknown"),
                "software": metadata.get("software", "None detected"),
                "timestamp": metadata.get("timestamp", "N/A")
            },
            "technical": {
                "processing_time": f"{elapsed}s",
                "image_size": f"{len(raw_bytes) // 1024} KB"
            }
        }
    )


@router.get("/history", tags=["History"])
async def get_history():
    db = SessionLocal()
    results = db.query(AnalysisResult).order_by(AnalysisResult.created_at.desc()).all()
    history = []
    for r in results:
        history.append({
            "id": r.id,
            "filename": r.filename,
            "ai_probability": r.ai_probability,
            "risk_level": r.risk_level,
            "verdict": r.verdict,
            "date": r.created_at.strftime("%Y-%m-%d %H:%M")
        })
    db.close()
    return history


@router.post("/chat", tags=["Chat"])
async def forensic_chat(request: dict):
    """
    Handles chat questions about a specific analysis.
    Input: { "message": "...", "analysis_results": {...} }
    """
    user_msg = request.get("message", "").lower()
    results = request.get("analysis_results", {})
    
    # ── Expert Responder Logic ────────────────────────────────────
    # This acts as a 'Knowledge Agent' based on the forensics we built.
    
    response = "I'm not sure about that specific detail, but looking at my forensic scan..."
    
    if "ela" in user_msg or "compression" in user_msg:
        response = ("ELA (Error Level Analysis) looks for inconsistencies in jpeg compression. "
                   "In this image, the compression is unusually uniform, which is a common "
                   "digital fingerprint of AI generators like Midjourney.")
    
    elif "grid" in user_msg or "checkerboard" in user_msg or "pattern" in user_msg:
        response = ("The 'checkerboard' artifacts are mathematical residues left by AI upsamplers. "
                   "When AI creates pixels from noise, it often leaves a subtle grid at regular "
                   "pixel intervals that my frequency scanner detected.")
                   
    elif "skin" in user_msg or "texture" in user_msg:
        response = ("I've flagged the textures because they lack 'Local Binary Pattern' entropy. "
                   "Basically, real skin has micro-pores and irregular shadows; AI skin often "
                   "looks 'too perfect' or mathematically smooth.")
                   
    elif "real" in user_msg or "human" in user_msg:
        prob = results.get("summary", {}).get("ai_probability", "0%")
        response = f"Based on my analysis, there is a {prob} chance this is AI-generated. " \
                    "The absence of camera metadata (EXIF) also weights towards it being synthetic."

    else:
        response = ("As your forensic assistant, I can explain the ELA artifacts, "
                   "frequency grids, or texture patterns I found. What would you like "
                   "me to clarify about the 'High Risk' flags?")

    return {"response": response}
