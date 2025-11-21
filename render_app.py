"""
DistilBART Summarizer using Hugging Face Inference API
No local model loading - uses HF API (much simpler deployment)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os

app = FastAPI(title="DistilBART Summarizer & Translation API", version="2.0")

# Hugging Face Inference API
HF_API_URL = "https://router.huggingface.co/hf-inference/models/sshleifer/distilbart-cnn-12-6"
HF_TRANSLATE_EN_UK_URL = "https://router.huggingface.co/hf-inference/models/Helsinki-NLP/opus-mt-en-uk"
HF_TOKEN = os.getenv("HF_TOKEN", "")  # Optional - works without token but with rate limits


class SummarizeRequest(BaseModel):
    text: str
    max_length: int = 150
    min_length: int = 30


class SummarizeResponse(BaseModel):
    summary: str
    original_length: int
    summary_length: int


class TranslateRequest(BaseModel):
    text: str


class TranslateResponse(BaseModel):
    translated_text: str
    original_text: str
    source_lang: str
    target_lang: str


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": ["summarization", "translation_en_uk"],
        "message": "DistilBART Summarizer & Translation API",
        "endpoints": {
            "/summarize": "Summarize English text",
            "/translate": "Translate English to Ukrainian"
        }
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


@app.post("/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    """
    Translate English text to Ukrainian

    Example:
    {
        "text": "Hello, how are you?"
    }
    """
    if not request.text or len(request.text.strip()) < 1:
        raise HTTPException(status_code=400, detail="Text is empty")

    try:
        # Call Hugging Face Inference API for translation
        headers = {}
        if HF_TOKEN:
            headers["Authorization"] = f"Bearer {HF_TOKEN}"

        payload = {
            "inputs": request.text
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(HF_TRANSLATE_EN_UK_URL, headers=headers, json=payload)

            if response.status_code == 503:
                raise HTTPException(
                    status_code=503,
                    detail="Translation model is loading on Hugging Face servers. Please retry in 20 seconds."
                )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Hugging Face API error: {response.text}"
                )

            result = response.json()

            # Extract translation from API response
            if isinstance(result, list) and len(result) > 0:
                translated = result[0].get("translation_text", "")
            else:
                raise HTTPException(status_code=500, detail="Unexpected API response format")

            return TranslateResponse(
                translated_text=translated,
                original_text=request.text,
                source_lang="en",
                target_lang="uk"
            )

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Request to Hugging Face API timed out")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@app.get("/health")
async def health():
    """Health check for monitoring"""
    return {
        "status": "healthy",
        "mode": "API (no local model)",
        "summarization_model": "distilbart-cnn-12-6",
        "translation_model": "Helsinki-NLP/opus-mt-en-uk"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
