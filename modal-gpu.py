"""
Option B Alternative: Deploy 70B on Modal (GPU platform)
Modal provides A100 GPUs perfect for large models.
Run: modal deploy modal-gpu.py
"""

import modal

app = modal.App("llama-70b-summarizer")

# Define GPU requirements
image = modal.Image.debian_slim().pip_install(
    "text-generation",
    "huggingface_hub",
)

@app.function(
    image=image,
    gpu=modal.gpu.A100(count=1, size="40GB"),  # or size="80GB" for more memory
    timeout=3600,
    container_idle_timeout=300,
    secrets=[modal.Secret.from_name("huggingface-token")],
)
@modal.web_endpoint(method="POST")
def generate(request: dict):
    """
    Endpoint for text generation using Llama 70B.

    Example request:
    {
        "prompt": "Summarize this text: ...",
        "max_tokens": 500,
        "temperature": 0.7
    }
    """
    from text_generation import Client

    client = Client(
        "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3.1-70B-Instruct",
        timeout=120
    )

    response = client.generate(
        request.get("prompt", ""),
        max_new_tokens=request.get("max_tokens", 500),
        temperature=request.get("temperature", 0.7),
    )

    return {"generated_text": response.generated_text}


@app.local_entrypoint()
def main():
    """Test the endpoint locally"""
    result = generate.remote({
        "prompt": "Summarize: Artificial intelligence is transforming software development...",
        "max_tokens": 100
    })
    print(result)
