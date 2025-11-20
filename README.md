# AI Summarizer - Multiple Deployment Options

Fast, cost-effective text summarization API with two deployment options.

## 🚀 Quick Start - Choose Your Deployment

### Option 1: Modal (Llama 3.1 8B) - Best Quality
- **Model**: Meta Llama 3.1 8B Instruct
- **Cost**: $10-50/month (pay-per-use)
- **RAM**: 16GB
- **Speed**: 2-5 seconds (warm), 2-5 min (cold start)
- **Best for**: Variable traffic, highest quality

👉 **[See MODAL_USAGE.md](MODAL_USAGE.md)** for setup

### Option 2: Render (DistilBART-CNN) - Best Value
- **Model**: DistilBART-CNN (optimized for summarization)
- **Cost**: $25/month (fixed)
- **RAM**: 2GB
- **Speed**: 1-3 seconds (no cold starts)
- **Best for**: Steady traffic, budget-friendly

👉 **[See RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)** for setup

## 📊 Comparison

| Feature | Modal (Llama 8B) | Render (DistilBART) |
|---------|------------------|---------------------|
| **Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Speed** | 2-5s (warm) | 1-3s |
| **Cost** | $10-50/mo (variable) | $25/mo (fixed) |
| **RAM** | 16GB | 2GB |
| **Cold Starts** | Yes (2-5 min) | No |
| **Scaling** | Automatic | Manual |
| **Best For** | High quality, variable traffic | Cost-effective, steady traffic |

## 📁 Project Structure

```
.
├── modal_app.py              # Modal deployment (Llama 8B)
├── render_app.py             # Render deployment (DistilBART)
├── requirements.txt          # Python dependencies
├── render.yaml               # Render configuration
├── test-request.json         # Sample test data
├── test_render_local.py      # Local testing script
├── MODAL_USAGE.md           # Modal deployment guide
├── RENDER_DEPLOYMENT.md     # Render deployment guide
└── README.md                # This file
```

## 🔧 Local Testing

### Test Render App (DistilBART)

```bash
# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn render_app:app --reload --port 8000

# Test in another terminal
python test_render_local.py
```

### Test Modal App (Llama 8B)

```bash
# Install Modal
pip install modal

# Setup Modal account
modal setup

# Deploy
modal deploy modal_app.py

# Test
curl -X POST https://your-workspace--llama-8b-summarizer-llamasummarizer-summarize.modal.run \
  -H "Content-Type: application/json" \
  -d @test-request.json
```

## 💡 When to Use Which?

### Use Modal (Llama 8B) if you:
- Need the highest quality summaries
- Have variable/unpredictable traffic
- Want automatic scaling
- Are okay with occasional cold starts
- Prefer pay-per-use pricing

### Use Render (DistilBART) if you:
- Need consistent performance (no cold starts)
- Have steady, predictable traffic
- Want fixed monthly costs
- Need to deploy on limited resources (2GB RAM)
- Want fast responses (1-3s)

## 🎯 Recommended Approach

**For production:** Start with Render (DistilBART) for cost-effectiveness and predictability. Upgrade to Modal (Llama 8B) if you need higher quality summaries.

**For experimentation:** Use Modal's pay-per-use model to test without commitment.

## 📝 API Usage

Both deployments provide the same API interface:

```bash
POST /summarize
{
  "text": "Your long text here...",
  "max_length": 150,    # DistilBART
  "max_tokens": 150,    # Modal (Llama)
  "min_length": 30,     # DistilBART only
  "temperature": 0.7    # Modal only
}
```

Response:
```json
{
  "summary": "AI is transforming software development...",
  "original_length": 425,
  "summary_length": 156
}
```

## 🔐 Environment Variables

Create `.env` file:

```bash
# For Modal deployment
HUGGING_FACE_HUB_TOKEN=your_token_here
```

Get your token from: https://huggingface.co/settings/tokens

## 📚 Documentation

- **[MODAL_USAGE.md](MODAL_USAGE.md)** - Complete Modal deployment guide
- **[RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)** - Complete Render deployment guide
- **[.env.example](.env.example)** - Environment variable template

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Models**:
  - Llama 3.1 8B Instruct (Modal)
  - DistilBART-CNN (Render)
- **Deployment**: Modal / Render
- **ML Library**: Transformers (Hugging Face)

## 📦 Dependencies

See `requirements.txt` for full list. Main dependencies:
- fastapi
- transformers
- torch
- uvicorn

## 🤝 Contributing

This is a personal project demonstrating different deployment strategies for AI models.

## 📄 License

MIT License - feel free to use this as a template for your own projects.

## 🆘 Support

- **Modal Issues**: Check [MODAL_USAGE.md](MODAL_USAGE.md) troubleshooting section
- **Render Issues**: Check [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) troubleshooting section
- **Modal Docs**: https://modal.com/docs
- **Render Docs**: https://render.com/docs

---

**Quick Links:**
- [Deploy to Modal](MODAL_USAGE.md)
- [Deploy to Render](RENDER_DEPLOYMENT.md)
- [Modal Dashboard](https://modal.com/apps)
- [Render Dashboard](https://dashboard.render.com/)
