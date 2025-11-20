"""
DistilBART Summarizer for Render
Optimized for 2GB RAM, 1 CPU deployment
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
import torch
import os

app = FastAPI(title="DistilBART Summarizer", version="1.0")

# Global model variable
summarizer = None


class SummarizeRequest(BaseModel):
    text: str
    max_length: int = 150
    min_length: int = 30


class SummarizeResponse(BaseModel):
    summary: str
    original_length: int
    summary_length: int


@app.on_event("startup")
async def load_model():
    """Load model once at startup"""
    global summarizer

    print("Loading DistilBART-CNN model...")

    # Use CPU and low memory mode
    device = 0 if torch.cuda.is_available() else -1  # -1 for CPU

    # Load the summarization pipeline
    summarizer = pipeline(
        "summarization",
        model="sshleifer/distilbart-cnn-12-6",
        device=device,
        torch_dtype=torch.float32,  # Use float32 for CPU
    )

    print("Model loaded successfully!")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model": "distilbart-cnn-12-6",
        "message": "DistilBART Summarizer API"
    }


@app.post("/summarize", response_model=SummarizeResponse)
async def summarize(request: SummarizeRequest):
    """
    Summarize text using DistilBART-CNN

    Example:
    ```
    POST /summarize
    {
        "text": "Your long text here...",
        "max_length": 150,
        "min_length": 30
    }
    ```
    """
    if not summarizer:
        raise HTTPException(status_code=503, detail="Model not loaded")

    if not request.text or len(request.text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Text is too short or empty")

    try:
        # Generate summary
        result = summarizer(
            request.text,
            max_length=request.max_length,
            min_length=request.min_length,
            do_sample=False,  # Deterministic for consistency
            truncation=True,  # Handle long inputs
        )

        summary_text = result[0]["summary_text"]

        return SummarizeResponse(
            summary=summary_text,
            original_length=len(request.text),
            summary_length=len(summary_text)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


@app.get("/health")
async def health():
    """Health check for monitoring"""
    return {
        "status": "healthy" if summarizer else "loading",
        "model_loaded": summarizer is not None
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
