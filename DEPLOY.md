# Deploy Llama 8B to Render

Quick deployment guide for your Llama 3.1 8B summarizer on Render.

## Prerequisites

- ✅ Render account (free tier works for Pro plan upgrade)
- ✅ GitHub account
- ✅ HuggingFace token (get from: https://huggingface.co/settings/tokens)
- ✅ Llama 3.1 access approved at https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct

## Step 1: Push to GitHub

```bash
# Add all files
git add .gitignore Dockerfile.small render-small.yaml README.md .env.example

# Commit
git commit -m "Add Llama 8B deployment config"

# Create GitHub repo (option A - via gh CLI):
gh repo create llama-summarizer --public --source=. --push

# OR (option B - manual):
# 1. Create repo at https://github.com/new (name: llama-summarizer)
# 2. Run:
git remote add origin https://github.com/YOUR_USERNAME/llama-summarizer.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy to Render

### Option A: Using Blueprint (Recommended)

1. Go to https://dashboard.render.com
2. Click **"New" → "Blueprint"**
3. Connect your GitHub repository
4. Render will auto-detect `render-small.yaml`
5. Before deploying, add environment variable:
   - Go to the service settings
   - **Environment** → **Add Secret**
   - Key: `HF_TOKEN`
   - Value: `<your_huggingface_token>`
6. Click **"Apply"**

### Option B: Manual Deploy

1. Go to https://dashboard.render.com
2. Click **"New" → "Web Service"**
3. Connect your GitHub repo
4. Configure:
   - **Name:** `llama-8b-summarizer`
   - **Region:** Oregon (or closest to you)
   - **Branch:** main
   - **Runtime:** Docker
   - **Dockerfile Path:** `./Dockerfile.small`
   - **Plan:** Pro ($25/mo - required for 32GB RAM)
5. **Environment Variables:**
   - Click **"Advanced"**
   - Add secret: `HF_TOKEN` = `<your_huggingface_token>`
6. Click **"Create Web Service"**

## Step 3: Monitor Deployment

1. **First deployment takes 10-15 minutes:**
   - Building Docker image: ~2 min
   - Downloading model (8GB): ~5-8 min
   - Loading model into memory: ~2-3 min

2. **Watch the logs:**
   - You'll see: "Connected" when ready
   - Health check endpoint: `https://your-app.onrender.com/health`

3. **Your app URL:**
   - `https://llama-8b-summarizer.onrender.com`

## Step 4: Test Your Deployment

```bash
# Save your Render URL
export RENDER_URL="https://your-app.onrender.com"

# Test health check
curl $RENDER_URL/health

# Test summarization
curl -X POST $RENDER_URL/generate \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": "Summarize: Artificial intelligence is transforming software development...",
    "parameters": {
      "max_new_tokens": 100,
      "temperature": 0.7
    }
  }'
```

## Expected Response

```json
{
  "generated_text": "AI is revolutionizing software development through machine learning models that assist with code completion, bug detection, and function generation, making developers more productive and programming more accessible."
}
```

## Troubleshooting

### Build fails with "platform not supported"
- ✅ **This is normal on Mac!** It works on Render's Linux servers
- Don't worry about local Docker errors

### "Model loading failed"
- Check HF_TOKEN is set correctly in Render dashboard
- Verify you've accepted the Llama 3.1 license

### Out of memory errors
- Verify you're on **Pro plan** (32GB RAM)
- Check logs for actual memory usage

### Slow first request
- First request after idle triggers model reload (~30 sec)
- Use Render's "keep alive" or implement a health check ping

## Cost Optimization

**Current setup:** ~$25-50/month

**To reduce costs:**
1. Use Render's free tier for testing (limited hours)
2. Scale down when not in use
3. Use serverless option (pay per request)

## Next Steps

- Add custom domain
- Implement request authentication
- Add rate limiting
- Monitor usage metrics
- Set up auto-scaling

## Support

- Render logs: https://dashboard.render.com
- Issues: Check README.md
- HF Model: https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct
