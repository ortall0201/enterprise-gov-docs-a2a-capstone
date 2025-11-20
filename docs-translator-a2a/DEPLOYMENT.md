# Render Deployment Guide for Docs Translator A2A Service

## 🔒 Security First!

**NEVER commit:**
- `.env` files with real API keys
- Any file containing `OPENAI_API_KEY` or secrets
- Service account JSON files

**ALWAYS:**
- Use Render's Environment Variables UI for secrets
- Keep `.env` files in `.gitignore`
- Use `.env.example` with placeholders only

---

## 🚀 Quick Deploy to Render

### Option 1: Using render.yaml (Recommended)

1. **Push to GitHub** (make sure `.env` is in `.gitignore`):
   ```bash
   git add .
   git commit -m "Add A2A service with Render config"
   git push origin main
   ```

2. **Connect to Render**:
   - Go to https://dashboard.render.com
   - Click "New +" → "Blueprint"
   - Connect your GitHub repo
   - Select `docs-translator-a2a/render.yaml`
   - Render will auto-detect the configuration

3. **Set Secret Environment Variable**:
   - In Render dashboard, go to your service
   - Click "Environment"
   - Add: `OPENAI_API_KEY` = `your_actual_openai_key` 🔒
   - Click "Save Changes"

4. **Deploy**:
   - Render will automatically build and deploy
   - Build should complete in 2-3 minutes (now that we removed CrewAI)

### Option 2: Manual Setup

1. **Create New Web Service**:
   - Dashboard → "New +" → "Web Service"
   - Connect GitHub repo
   - Root Directory: `docs-translator-a2a`

2. **Configure Build**:
   - **Runtime**: Python 3
   - **Build Command**:
     ```bash
     pip install --upgrade pip && pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     python src/a2a_server.py
     ```

3. **Set Environment Variables** (in Render UI):
   ```
   OPENAI_API_KEY=<your_actual_key>        🔒 SECRET
   OPENAI_MODEL=gpt-4o
   A2A_SERVICE_HOST=0.0.0.0
   A2A_SERVICE_PORT=8001
   LOG_LEVEL=INFO
   VENDOR_NAME=Docs Translator
   VENDOR_URL=https://your-service.onrender.com
   VENDOR_CONTACT=your@email.com
   ```

4. **Deploy**:
   - Click "Create Web Service"
   - Wait 2-3 minutes for build

---

## ✅ Verify Deployment

Once deployed, test these endpoints:

### 1. Health Check
```bash
curl https://your-service.onrender.com/health
```

**Expected**:
```json
{
  "status": "healthy",
  "service": "docs-translator-a2a",
  "version": "1.0.0",
  "framework": "CrewAI",
  "a2a_enabled": true,
  "openai_configured": true
}
```

### 2. Agent Card
```bash
curl https://your-service.onrender.com/.well-known/agent-card.json
```

**Expected**: JSON with agent capabilities

### 3. Root Info
```bash
curl https://your-service.onrender.com/
```

---

## 🔧 Troubleshooting

### Build Stuck or Timing Out

**Fixed!** We removed heavy dependencies (CrewAI, google-cloud-aiplatform).

If still stuck:
- Check Render logs for errors
- Verify Python version is 3.11
- Ensure requirements.txt has exact versions

### Service Crashes on Start

**Check logs** for:
```
⚠️  OPENAI_API_KEY not set - translations will fail!
```

**Fix**: Add OPENAI_API_KEY in Render Environment Variables (dashboard)

### Agent Card 404

**Issue**: Service not running or wrong port

**Fix**:
- Check logs: `uvicorn running on 0.0.0.0:8001`
- Verify port is 8001 in environment variables

### Translation Fails

**Check**:
1. OPENAI_API_KEY is set correctly (no extra spaces)
2. OpenAI API has credits/billing enabled
3. Model name is correct (`gpt-4o` or `gpt-4o-mini`)

---

## 📊 Expected Build Time

With optimized dependencies:
- **Build**: 2-3 minutes
- **Deploy**: 30 seconds
- **Total**: ~3 minutes

Old build with CrewAI: 10-15 minutes (often timeout)

---

## 🔄 Update Your Enterprise Repo

Once deployed, update your enterprise repo's `.env`:

```bash
# Point to production A2A service on Render
VENDOR_SERVER_HOST=your-service.onrender.com
VENDOR_SERVER_PORT=443
```

Or update `tools/vendor_connector.py`:
```python
vendor_url = "https://your-service.onrender.com"
```

---

## 🎯 Production Checklist

Before going live:

- [ ] OPENAI_API_KEY set as secret in Render (not in code)
- [ ] `.env` file is in `.gitignore`
- [ ] Health check endpoint working
- [ ] Agent Card accessible
- [ ] Test translation with masked PII
- [ ] Monitor usage and costs (OpenAI API)
- [ ] Consider upgrading from Free tier (Free tier sleeps after 15min)

---

## 💰 Render Pricing (as of 2024)

- **Free Tier**: $0/month (sleeps after 15min inactivity)
- **Starter**: $7/month (always on, 512MB RAM)
- **Standard**: $25/month (2GB RAM, auto-scaling)

**Recommendation for VaaS**: Start with Free tier for testing, upgrade to Starter for production.

---

## 🔗 Important URLs (After Deployment)

Replace `your-service` with your actual Render service name:

- **Service URL**: `https://your-service.onrender.com`
- **Agent Card**: `https://your-service.onrender.com/.well-known/agent-card.json`
- **Health**: `https://your-service.onrender.com/health`
- **Logs**: Render dashboard → Your Service → Logs

---

## 🛡️ Security Best Practices

1. **Never commit secrets to Git**
   - Add `.env` to `.gitignore`
   - Use Render's Environment Variables UI

2. **Rotate API keys regularly**
   - OpenAI: https://platform.openai.com/api-keys
   - Update in Render dashboard

3. **Monitor API usage**
   - OpenAI Dashboard: Track costs
   - Set usage limits if needed

4. **Enable HTTPS only**
   - Render provides free SSL
   - Never use HTTP in production

5. **Restrict CORS (if needed)**
   - Update `a2a_server.py` CORS settings
   - Whitelist only enterprise domains

---

## 📞 Support

- **Render Docs**: https://docs.render.com
- **Render Community**: https://community.render.com
- **OpenAI Status**: https://status.openai.com

---

**Built for the Kaggle AI Agents Intensive VaaS Capstone** 🎓
