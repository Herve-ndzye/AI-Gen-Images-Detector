"""
AI Image Verification Service - FastAPI Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.analyze import router as analyze_router
from routes.auth import router as auth_router

app = FastAPI(
    title="AI Image Verification Service",
    description="Analyzes whether an uploaded image is AI-generated and returns detailed insights.",
    version="1.0.0",
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "AI Image Verification Service"}
