"""
DistilBART Summarizer using Hugging Face Inference API
No local model loading - uses HF API (much simpler deployment)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os

app = FastAPI(title="DistilBART Summarizer (API)", version="1.0")

# Hugging Face Inference API
HF_API_URL = "https://router.huggingface.co/hf-inference/models/sshleifer/distilbart-cnn-12-6"
HF_TOKEN = os.getenv("HF_TOKEN", "")  # Optional - works without token but with rate limits


class SummarizeRequest(BaseModel):
    text: str
    max_length: int = 150
    min_length: int = 30


class SummarizeResponse(BaseModel):
    summary: str
    original_length: int
    summary_length: int


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model": "distilbart-cnn-12-6",
        "message": "DistilBART Summarizer API (Hugging Face Inference API)"
    }


@app.post("/summarize", response_model=SummarizeResponse)
async def summarize(request: SummarizeRequest):
    """
    Summarize text using DistilBART via Hugging Face Inference API

    No local model needed - uses HF API!
    """
    if not request.text or len(request.text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Text is too short or empty")

    try:
        # Call Hugging Face Inference API
        headers = {}
        if HF_TOKEN:
            headers["Authorization"] = f"Bearer {HF_TOKEN}"

        payload = {
            "inputs": request.text,
            "parameters": {
                "max_length": request.max_length,
                "min_length": request.min_length,
                "do_sample": False,
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(HF_API_URL, headers=headers, json=payload)

            if response.status_code == 503:
                raise HTTPException(
                    status_code=503,
                    detail="Model is loading on Hugging Face servers. Please retry in 20 seconds."
                )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Hugging Face API error: {response.text}"
                )

            result = response.json()

            # Extract summary from API response
            if isinstance(result, list) and len(result) > 0:
                summary_text = result[0].get("summary_text", "")
            else:
                raise HTTPException(status_code=500, detail="Unexpected API response format")

            return SummarizeResponse(
                summary=summary_text,
                original_length=len(request.text),
                summary_length=len(summary_text)
            )

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Request to Hugging Face API timed out")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


@app.get("/health")
async def health():
    """Health check for monitoring"""
    return {
        "status": "healthy",
        "mode": "API (no local model)",
        "api_endpoint": HF_API_URL
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
