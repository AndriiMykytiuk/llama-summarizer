# Modal Deployment - Usage Guide

## ✅ Deployment Status: LIVE

**API Endpoint:** `https://andrij-mykytuk--llama-8b-summarizer-summarize.modal.run`

**Dashboard:** https://modal.com/apps/andrij-mykytuk/main/deployed/llama-8b-summarizer

## How It Works

- **Serverless:** Only runs when you send requests (auto-scales to zero)
- **Pay-per-use:** Only charged when generating text (~$0.10-0.20/hour)
- **Cold starts:** First request takes 2-5 minutes (model download), then fast (~2-5 seconds)
- **Warm period:** Stays loaded for 5 minutes after last request

## Usage Examples

### cURL
```bash
curl -X POST https://andrij-mykytuk--llama-8b-summarizer-summarize.modal.run \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your long text here...",
    "max_tokens": 150,
    "temperature": 0.7
  }'
```

### Python
```python
import requests

def summarize_text(text, max_tokens=150):
    response = requests.post(
        "https://andrij-mykytuk--llama-8b-summarizer-summarize.modal.run",
        json={
            "text": text,
            "max_tokens": max_tokens,
            "temperature": 0.7
        },
        timeout=180  # 3 minutes for cold starts
    )
    return response.json()

# Example
text = """
Artificial intelligence is rapidly transforming industries...
"""

result = summarize_text(text)
print(f"Summary: {result['summary']}")
print(f"Original: {result['original_length']} chars")
print(f"Summary: {result['summary_length']} chars")
```

### JavaScript
```javascript
async function summarize(text, maxTokens = 150) {
  const response = await fetch(
    'https://andrij-mykytuk--llama-8b-summarizer-summarize.modal.run',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: text,
        max_tokens: maxTokens,
        temperature: 0.7
      })
    }
  );

  return await response.json();
}

// Example
const result = await summarize("Your long text here...");
console.log('Summary:', result.summary);
```

## Cost Estimation

### Compute Costs (CPU - 4 cores, 16GB RAM)
- **Per hour:** ~$0.10-0.20
- **Per request:** ~$0.001-0.01 (depending on length)
- **Idle:** $0 (auto-scales to zero)

### Monthly Estimates
- **Light usage** (10 requests/day): ~$3-10/mo
- **Medium usage** (100 requests/day): ~$30-50/mo
- **Heavy usage** (1000 requests/day): ~$100-200/mo

**Much cheaper than Render** ($225/mo minimum for 70B!)

## Performance

| Scenario | Time | Cost |
|----------|------|------|
| Cold start (first request) | 2-5 min | ~$0.01 |
| Warm requests | 2-5 sec | ~$0.001 |
| Model stays warm for | 5 minutes | after last request |

## Tips for Production

### 1. Keep It Warm
```python
# Ping every 4 minutes to keep warm
import schedule
import requests

def keep_warm():
    requests.post(url, json={"text": "ping", "max_tokens": 10})

schedule.every(4).minutes.do(keep_warm)
```

### 2. Handle Cold Starts
```python
import requests
from tenacity import retry, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(3), wait=wait_fixed(30))
def summarize_with_retry(text):
    response = requests.post(url, json={"text": text}, timeout=180)
    response.raise_for_status()
    return response.json()
```

### 3. Add Rate Limiting
```python
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=10, period=60)  # 10 requests per minute
def summarize(text):
    # your code here
    pass
```

## Monitoring

### View Logs
```bash
modal app logs llama-8b-summarizer
```

### Check Usage
Visit: https://modal.com/billing

### Update Deployment
```bash
# Edit modal_app.py, then:
modal deploy modal_app.py
```

## Troubleshooting

### Timeout on First Request
- **Normal!** First request takes 2-5 min
- Increase timeout to 180-300 seconds
- Subsequent requests will be fast

### "App stopped" Error
- Container scaled to zero (idle timeout)
- Send another request to restart
- Takes 2-5 min to warm up again

### Out of Memory
- Reduce `max_tokens` parameter
- Current config uses 16GB RAM (should be fine)

### Slow Responses
- CPU inference is slower than GPU
- Upgrade to GPU for 10x speedup:
  ```python
  gpu="T4"  # in modal_app.py
  ```
- GPU costs more (~$0.50/hour)

## Upgrading to GPU

If you need faster responses, edit `modal_app.py`:

```python
@app.cls(
    gpu="T4",  # or "A10G" for more power
    # cpu=4.0,  # Remove this line
    memory=16384,
    # ... rest stays the same
)
```

Then redeploy:
```bash
modal deploy modal_app.py
```

**GPU speeds:**
- T4: ~20-30 tokens/sec (~$0.50/hour)
- A10G: ~40-60 tokens/sec (~$1.10/hour)

## Next Steps

1. **Test the endpoint** (allow 2-5 min for first request)
2. **Integrate into your app**
3. **Monitor usage and costs** in Modal dashboard
4. **Upgrade to GPU** if speed is critical
5. **Add authentication** for production use

## Support

- Modal docs: https://modal.com/docs
- Dashboard: https://modal.com/apps/andrij-mykytuk
- Logs: `modal app logs llama-8b-summarizer`
