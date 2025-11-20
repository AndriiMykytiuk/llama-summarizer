# Render Deployment Guide - DistilBART Summarizer

## Model: DistilBART-CNN (2GB RAM optimized)

**Perfect for Render Standard Plan**: 2GB RAM, 1 CPU, $25/month

## Why DistilBART-CNN?

- **Small**: ~600MB RAM usage (fits comfortably in 2GB)
- **Fast**: Optimized for CPU inference
- **Quality**: Specifically trained for summarization
- **Stable**: No memory issues on small instances

## Deployment Steps

### 1. Push to GitHub

```bash
git add render_app.py requirements.txt render.yaml
git commit -m "Add Render deployment with DistilBART"
git push origin main
```

### 2. Deploy on Render

1. Go to https://dashboard.render.com/
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Render will auto-detect `render.yaml`
5. Click "Create Web Service"

### 3. Configuration (if not using render.yaml)

If you want to configure manually:

- **Name**: distilbart-summarizer
- **Runtime**: Python 3
- **Plan**: Starter ($25/mo - 2GB RAM, 1 CPU)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn render_app:app --host 0.0.0.0 --port $PORT`
- **Health Check Path**: `/health`

## First Deployment

- **Initial build**: 5-10 minutes (downloads model)
- **Subsequent deploys**: 2-5 minutes
- **Model stays in memory**: No cold starts!

## API Usage

### Endpoint

```
https://your-app-name.onrender.com/summarize
```

### Example Request (cURL)

```bash
curl -X POST https://your-app-name.onrender.com/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your long text here...",
    "max_length": 150,
    "min_length": 30
  }'
```

### Example Request (Python)

```python
import requests

response = requests.post(
    "https://your-app-name.onrender.com/summarize",
    json={
        "text": """
        Artificial intelligence is rapidly transforming the software
        development industry. Machine learning models are now being used
        to assist developers with code completion, bug detection, and
        even generating entire functions.
        """,
        "max_length": 100,
        "min_length": 30
    }
)

result = response.json()
print(f"Summary: {result['summary']}")
print(f"Original length: {result['original_length']} chars")
print(f"Summary length: {result['summary_length']} chars")
```

### Example Response

```json
{
  "summary": "Artificial intelligence is transforming software development. ML models assist with code completion and bug detection. This makes developers more productive.",
  "original_length": 425,
  "summary_length": 156
}
```

## Performance on 2GB RAM

### Memory Usage
- **At startup**: ~800MB-1.2GB (model loading)
- **During inference**: ~1-1.5GB
- **Available headroom**: ~500MB for system

### Speed
- **Cold start**: None (model stays loaded)
- **First request**: 1-3 seconds
- **Subsequent requests**: 0.5-2 seconds
- **Long texts (1000+ words)**: 2-5 seconds

## Cost Comparison

| Platform | Plan | RAM | CPU | Cost/Month | Model |
|----------|------|-----|-----|------------|-------|
| **Render** | Standard | 2GB | 1 | $25 | DistilBART-CNN |
| Modal | CPU | 16GB | 4 | ~$10-50 | Llama 8B (pay-per-use) |
| Render | Pro | 8GB | 2 | $85 | Llama 8B possible |

## Monitoring

### Health Check
```bash
curl https://your-app-name.onrender.com/health
```

Response:
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### Logs
View logs in Render Dashboard: https://dashboard.render.com/

## Troubleshooting

### Out of Memory
- **Solution**: Model is optimized for 2GB, but if issues occur:
  1. Restart the service in Render dashboard
  2. Check for memory leaks in logs
  3. Consider upgrading to 4GB plan ($85/mo)

### Slow Responses
- **Expected**: CPU inference is slower than GPU
- **Typical**: 1-3 seconds per request
- **Long texts**: Up to 5 seconds
- **Solution**: Use shorter input texts or upgrade to GPU plan

### Build Failures
- **Check**: Python version is 3.11
- **Check**: All dependencies in requirements.txt
- **Solution**: View build logs in Render dashboard

## Scaling

### Traffic Handling
- **Standard plan**: ~100-200 requests/hour comfortably
- **For higher traffic**: Upgrade to Pro plan or use autoscaling

### Autoscaling
Render handles this automatically on paid plans.

## Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn render_app:app --reload --port 8000

# Test
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text here..."}'
```

## Comparison: Modal vs Render

| Feature | Modal (Llama 8B) | Render (DistilBART) |
|---------|------------------|---------------------|
| **Cost** | ~$3-200/mo (usage-based) | $25/mo (fixed) |
| **RAM** | 16GB | 2GB |
| **Model Quality** | Excellent | Good |
| **Speed** | 2-5s (warm) | 1-3s |
| **Cold Starts** | 2-5 min | None |
| **Scaling** | Automatic | Manual |
| **Best For** | Variable traffic | Steady traffic |

## Next Steps

1. Deploy to Render using the steps above
2. Test the `/summarize` endpoint
3. Integrate into your application
4. Monitor performance in Render dashboard

## Support

- Render Docs: https://render.com/docs
- Dashboard: https://dashboard.render.com/
- Status: https://status.render.com/
