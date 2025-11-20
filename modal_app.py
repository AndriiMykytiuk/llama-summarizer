"""
Llama 3.1 8B Summarizer on Modal
Cost-effective serverless deployment
"""

import modal

# Create Modal app
app = modal.App("llama-8b-summarizer")

# Define the container image with all dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "transformers==4.44.2",
        "torch==2.4.1",
        "accelerate==0.34.2",
        "sentencepiece==0.2.0",
        "protobuf==5.28.2",
        "fastapi==0.115.0",
        "pydantic==2.9.0",
    )
)

# Model configuration
MODEL_ID = "meta-llama/Meta-Llama-3.1-8B-Instruct"
MODEL_REVISION = "main"


@app.cls(
    image=image,
    gpu=None,  # Use CPU for cost savings (change to "T4" or "A10G" for GPU)
    cpu=4.0,   # 4 CPUs for good performance
    memory=16384,  # 16GB RAM - enough for 8B model
    secrets=[modal.Secret.from_name("huggingface")],
    timeout=3600,
    min_containers=1,  # Keep 1 container warm
)
class LlamaSummarizer:
    @modal.enter()
    def load_model(self):
        """Load model when container starts"""
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch

        print(f"Loading model: {MODEL_ID}")

        self.tokenizer = AutoTokenizer.from_pretrained(
            MODEL_ID,
            revision=MODEL_REVISION,
            token=True,  # Uses HUGGING_FACE_HUB_TOKEN from secrets
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            revision=MODEL_REVISION,
            token=True,
            torch_dtype=torch.float16,  # Use half precision to save memory
            device_map="cpu",  # or "auto" for GPU
            low_cpu_mem_usage=True,
        )

        print("Model loaded successfully!")

    @modal.method()
    def generate(self, prompt: str, max_tokens: int = 150, temperature: float = 0.7):
        """Generate text completion"""
        from transformers import GenerationConfig

        # Format prompt for instruction model
        messages = [{"role": "user", "content": prompt}]
        input_text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        # Tokenize
        inputs = self.tokenizer(input_text, return_tensors="pt")

        # Generate
        generation_config = GenerationConfig(
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=True,
            top_p=0.9,
            repetition_penalty=1.1,
        )

        print(f"Generating response for: {prompt[:100]}...")

        outputs = self.model.generate(
            **inputs,
            generation_config=generation_config,
        )

        # Decode
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract just the generated part (after the prompt)
        generated_text = response[len(input_text):].strip()

        return generated_text

    @modal.fastapi_endpoint(method="POST")
    def summarize(self, data: dict):
        """
        Web endpoint for summarization - uses the already-loaded model

        POST https://your-workspace--llama-8b-summarizer-summarize.modal.run

        Body:
        {
            "text": "Your long text here...",
            "max_tokens": 150,  // optional
            "temperature": 0.7  // optional
        }
        """
        text = data.get("text", "")
        max_tokens = data.get("max_tokens", 150)
        temperature = data.get("temperature", 0.7)

        if not text:
            return {"error": "No text provided"}

        # Create summarization prompt
        prompt = f"Summarize the following text in 2-3 clear sentences:\n\n{text}"

        # Generate summary using the already-loaded model in THIS container
        summary = self.generate(prompt, max_tokens, temperature)

        return {
            "summary": summary,
            "original_length": len(text),
            "summary_length": len(summary),
        }


@app.local_entrypoint()
def main():
    """Test the summarizer locally"""

    test_text = """
    Artificial intelligence is rapidly transforming the software development industry.
    Machine learning models are now being used to assist developers with code completion,
    bug detection, and even generating entire functions. This technology promises to make
    developers more productive while also making programming more accessible to newcomers.
    Large language models like GPT-4 and Claude can understand context and generate human-like
    code, significantly reducing development time for routine tasks.
    """

    print("Testing summarizer...")
    summarizer = LlamaSummarizer()
    result = summarizer.summarize.remote({"text": test_text})
    print(f"\nOriginal text length: {result['original_length']} chars")
    print(f"Summary length: {result['summary_length']} chars")
    print(f"\nSummary:\n{result['summary']}")
