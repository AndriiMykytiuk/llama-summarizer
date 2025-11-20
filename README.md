# Llama Summarizer Deployment

Two deployment options for running Llama models with different trade-offs.

## Quick Comparison

| Feature | Option A (8B) | Option B (70B) |
|---------|---------------|----------------|
| **Model** | Llama 3.1 8B | Llama 3.1 70B |
| **Quality** | Excellent | Best-in-class |
| **Speed** | ~50-100 tokens/sec | ~20-40 tokens/sec |
| **Memory** | ~16GB | ~40GB VRAM |
| **Cost (est.)** | $25-50/mo | $200-500/mo |
| **Platform** | Render Pro ✅ | Modal/RunPod/Replicate |
| **Setup Time** | 5 minutes | 15-30 minutes |

## Option A: Llama 3.1 8B (Recommended for Most Use Cases)

**Best for:** Production apps, tight budgets, fast response times

### Deploy to Render

1. **Set up Hugging Face token:**
   ```bash
   # Get token from https://huggingface.co/settings/tokens
   # Add to Render dashboard: Settings → Environment → Add Secret
   # Name: HF_TOKEN
   ```

2. **Deploy:**
   ```bash
   # Use Dockerfile.small and render-small.yaml
   git init
   git add Dockerfile.small render-small.yaml
   git commit -m "Add Llama 8B config"
   git push

   # Or use Render Blueprint:
   # Point to render-small.yaml in Render dashboard
   ```

3. **Test:**
   ```bash
   curl https://your-app.onrender.com/generate \
     -X POST \
     -H "Content-Type: application/json" \
     -d '{"inputs": "Summarize: [your text here]", "parameters": {"max_new_tokens": 200}}'
   ```

### Local Testing

```bash
docker build -f Dockerfile.small -t llama-8b .
docker run -p 8080:8080 \
  -e HUGGING_FACE_HUB_TOKEN=your_token_here \
  llama-8b
```

## Option B: Llama 3.1 70B (Maximum Quality)

**Best for:** Research, high-quality content generation, complex reasoning

### ⚠️ Important: Render Limitations

Render doesn't offer GPU instances suitable for 70B models. Use one of these alternatives:

### B1: Modal (Recommended)

**Pros:** Serverless, auto-scaling, pay-per-use
**Cost:** ~$1-2 per hour when running

```bash
# Install Modal
pip install modal

# Set up token
modal secret create huggingface-token HUGGINGFACE_TOKEN=your_token

# Deploy
modal deploy modal-gpu.py

# Your endpoint will be at:
# https://your-workspace--llama-70b-summarizer-generate.modal.run
```

### B2: RunPod (Cost-Effective GPU)

**Pros:** Cheaper than Modal, persistent instances
**Cost:** ~$0.69/hour for A100 40GB

1. Sign up at [runpod.io](https://runpod.io)
2. Deploy using template:
   - GPU: A100 40GB
   - Docker Image: `ghcr.io/huggingface/text-generation-inference:2.4.0`
   - Environment variables:
     ```
     MODEL_ID=meta-llama/Meta-Llama-3.1-70B-Instruct
     QUANTIZE=bitsandbytes-nf4
     HUGGING_FACE_HUB_TOKEN=your_token
     ```

### B3: Replicate (Easiest)

**Pros:** No infrastructure management, instant deployment
**Cost:** Pay per request (~$0.0001/token)

```python
import replicate

output = replicate.run(
    "meta/meta-llama-3.1-70b-instruct",
    input={"prompt": "Summarize: ..."}
)
```

## Cost Analysis

### Monthly Estimates (24/7 uptime)

**Option A (Render Pro):**
- Render Pro: $25/mo
- Total: **$25-50/mo**

**Option B (RunPod A100):**
- A100 40GB: ~$500/mo (24/7)
- **Recommended:** Use serverless (Modal) or on-demand for <$100/mo

**Option B (Modal Serverless):**
- Only pay when generating
- ~$50-200/mo for typical usage
- **Most cost-effective for 70B**

## Which Should You Choose?

### Choose Option A (8B) if:
- ✅ Budget is important
- ✅ Need fast response times
- ✅ Quality of Llama 8B is sufficient (it's very good!)
- ✅ Want simple Render deployment

### Choose Option B (70B) if:
- ✅ Need absolute best quality
- ✅ Complex reasoning/analysis required
- ✅ Willing to use Modal/RunPod
- ✅ Budget allows $100+/mo

## Next Steps

1. **Try Option A first** - deploy in 5 minutes, test quality
2. **If quality insufficient** - upgrade to Option B
3. **Monitor costs** - use Modal serverless for 70B to control costs

## Troubleshooting

### Model Download Issues
```bash
# Verify HF token has access to gated models
# Visit: https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct
# Click "Agree and access repository"
```

### Memory Issues (Option A)
```bash
# Reduce max_total_tokens in Dockerfile.small
ENV MAX_TOTAL_TOKENS=4096
```

### GPU Issues (Option B)
```bash
# Verify GPU is detected
docker run --gpus all nvidia/cuda:12.0-base nvidia-smi
```

## API Usage Examples

### Python
```python
import requests

response = requests.post(
    "https://your-endpoint/generate",
    json={
        "inputs": "Summarize this article: ...",
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7,
            "top_p": 0.9
        }
    }
)
print(response.json())
```

### JavaScript
```javascript
const response = await fetch('https://your-endpoint/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    inputs: 'Summarize: ...',
    parameters: { max_new_tokens: 200 }
  })
});
const data = await response.json();
```

## Support

- Render docs: https://render.com/docs
- TGI docs: https://huggingface.co/docs/text-generation-inference
- Modal docs: https://modal.com/docs
