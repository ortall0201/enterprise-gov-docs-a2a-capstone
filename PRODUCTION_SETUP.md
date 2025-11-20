# Production Setup Guide

## 🎉 Your A2A Server is Live!

**Production URL**: https://docs-translator-a2a.onrender.com

### Endpoints Available:

| Endpoint | URL | Purpose |
|----------|-----|---------|
| **Agent Card** | `https://docs-translator-a2a.onrender.com/.well-known/agent-card.json` | A2A discovery |
| **Health** | `https://docs-translator-a2a.onrender.com/health` | Service health |
| **Invoke** | `https://docs-translator-a2a.onrender.com/invoke` | Non-streaming API |
| **Stream** | `https://docs-translator-a2a.onrender.com/stream` | Streaming API |

---

## 📝 Configure Your Enterprise App

### Option 1: Using Environment Variables (Recommended)

1. **Copy `.env.example` to `.env`**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env`** and set:
   ```bash
   # Your Google AI API Key
   GOOGLE_API_KEY=your_actual_google_api_key_here

   # Production A2A Server (on Render)
   VENDOR_SERVER_HOST=docs-translator-a2a.onrender.com
   VENDOR_SERVER_PORT=443

   LOG_LEVEL=INFO
   ```

3. **Run your enterprise app**:
   ```bash
   python main.py
   ```

### Option 2: Hardcode in vendor_connector.py

If you want to hardcode the production URL:

```python
# In tools/vendor_connector.py, line 46-47:
host = vendor_host or "docs-translator-a2a.onrender.com"
port = vendor_port or 443
```

---

## 🧪 Test the Connection

### 1. Test Agent Card Directly
```bash
curl https://docs-translator-a2a.onrender.com/.well-known/agent-card.json
```

**Expected**: JSON with agent capabilities

### 2. Test Health Endpoint
```bash
curl https://docs-translator-a2a.onrender.com/health
```

**Expected**:
```json
{
  "status": "healthy",
  "service": "docs-translator-a2a",
  "a2a_enabled": true,
  "openai_configured": true
}
```

### 3. Test Translation via Invoke
```bash
curl -X POST https://docs-translator-a2a.onrender.com/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "translate_document",
    "parameters": {
      "text": "Hola mundo",
      "source_language": "es",
      "target_language": "en",
      "document_type": "general"
    }
  }'
```

**Expected**: Translation result

### 4. Test End-to-End with Enterprise App
```bash
# Make sure .env has GOOGLE_API_KEY and VENDOR_SERVER_HOST set
python main.py
```

**Expected Flow**:
```
[A2A Connector] Configuring remote vendor connection:
    Vendor URL: https://docs-translator-a2a.onrender.com
    Agent Card: https://docs-translator-a2a.onrender.com/.well-known/agent-card.json
    Protocol: A2A over HTTPS
✓ Vendor A2A server is online and ready

[STAGE 1: DOCUMENT INTAKE]
...
[STAGE 2: DOCUMENT PROCESSING WITH A2A]
   → Step 3: A2A vendor call [CROSS-ORG BOUNDARY]
   ✓ Translation received from vendor
```

---

## 🔄 Switching Between Local and Production

### For Local Testing (with docs-translator-a2a running locally):
```bash
# .env
VENDOR_SERVER_HOST=localhost
VENDOR_SERVER_PORT=8001
```

### For Production (Render deployment):
```bash
# .env
VENDOR_SERVER_HOST=docs-translator-a2a.onrender.com
VENDOR_SERVER_PORT=443
```

The `vendor_connector.py` automatically:
- Uses **HTTPS** for port 443
- Uses **HTTP** for other ports
- Omits port number in URL for standard ports (443, 80)

---

## 📊 Monitoring Production Service

### Render Dashboard
- **URL**: https://dashboard.render.com
- **Logs**: View real-time logs for debugging
- **Metrics**: CPU, memory, request count
- **Environment Variables**: Manage secrets securely

### Key Metrics to Monitor:
- **Response Time**: Should be ~3-5 seconds for translations
- **Error Rate**: Check for OpenAI API errors
- **Uptime**: Free tier sleeps after 15min, Starter tier always on

---

## 💰 Cost Considerations

### Render Costs:
- **Free Tier**: $0/month (sleeps after 15min inactivity)
- **Starter**: $7/month (always on, 512MB RAM) ⭐ Recommended
- **Standard**: $25/month (2GB RAM, auto-scaling)

### OpenAI Costs:
- **GPT-4o**: ~$5 per 1M input tokens, $15 per 1M output tokens
- **GPT-4o-mini**: ~$0.15 per 1M input tokens, $0.60 per 1M output tokens
- **Recommendation**: Start with `gpt-4o-mini` for testing

### Cost Optimization:
1. Use `gpt-4o-mini` in OPENAI_MODEL env var on Render
2. Set usage limits in OpenAI dashboard
3. Cache common translations if needed
4. Monitor usage via OpenAI dashboard

---

## 🔒 Security Best Practices

### Production Checklist:
- ✅ OPENAI_API_KEY stored as secret in Render (not in code)
- ✅ `.env` file in `.gitignore` (never commit secrets)
- ✅ HTTPS enforced (port 443)
- ✅ CORS configured appropriately in `a2a_server.py`
- ⚠️ Consider adding authentication (currently open)
- ⚠️ Consider rate limiting for production
- ⚠️ Monitor API usage and costs

### Future Enhancements:
1. **Add API Key Auth**: Require API key for `/invoke` and `/stream`
2. **Rate Limiting**: Prevent abuse with request limits
3. **Request Logging**: Track usage per customer
4. **Custom Domain**: Use your own domain instead of `.onrender.com`
5. **Multi-region**: Deploy to multiple regions for redundancy

---

## 🐛 Troubleshooting

### "Connection refused" or "Cannot connect to vendor"
- **Check**: Is the service running on Render?
- **Check**: Is VENDOR_SERVER_HOST correct in .env?
- **Check**: Is port 443 (not 8001) in production?
- **Test**: `curl https://docs-translator-a2a.onrender.com/health`

### "Translation failed" or "500 Internal Server Error"
- **Check Render logs**: Look for OpenAI API errors
- **Check**: OPENAI_API_KEY is set in Render environment variables
- **Check**: OpenAI account has credits/billing enabled
- **Test**: Call `/health` to verify `"openai_configured": true`

### "Agent Card not found" (404)
- **Check**: URL is exactly `/.well-known/agent-card.json`
- **Check**: Service is running (view Render logs)
- **Test**: `curl -I https://docs-translator-a2a.onrender.com/.well-known/agent-card.json`

### Service is slow (Free tier)
- **Issue**: Free tier cold starts take 30-60 seconds after sleep
- **Solution**: Upgrade to Starter tier ($7/mo) for always-on service
- **Workaround**: Ping `/health` every 10 minutes to keep it warm

---

## 📞 Support

- **Render Documentation**: https://docs.render.com
- **OpenAI Status**: https://status.openai.com
- **Repository Issues**: https://github.com/ortall0201/enterprise-gov-docs-a2a-capstone/issues

---

## 🎯 Next Steps

1. ✅ A2A server deployed to Render
2. ✅ Agent Card accessible
3. ⏭️ Configure enterprise app `.env` with production URL
4. ⏭️ Test end-to-end A2A translation flow
5. ⏭️ Monitor costs and usage
6. ⏭️ Consider upgrading to Starter tier for production
7. ⏭️ Add authentication for production use

---

**Congratulations! Your VaaS A2A service is production-ready!** 🎉

Built for the **Kaggle AI Agents Intensive Capstone Project**
