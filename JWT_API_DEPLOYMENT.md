# JWT API Deployment Guide

## Overview

This guide covers deploying the Free Fire JWT Generator API based on kaifcodec's implementation. The JWT API is essential for generating authentication tokens for guest accounts.

---

## 🎯 Quick Start

### Prerequisites
- Guest accounts in `freefire/guests_manager/guests_converted.json`
- Python 3.11+ (for local testing)
- Railway/Render/Fly.io account (for deployment)

### Test Locally First

```bash
# 1. Install dependencies
cd jwt_api
pip install -r requirements.txt

# 2. Start JWT API
uvicorn main:app --host 0.0.0.0 --port 3000

# 3. Test in another terminal
cd ..
python test_jwt_api.py
```

---

## 🚀 Deployment Options

### Option 1: Railway (Recommended)

**Pros**: Easy, automatic deploys, free tier available
**Cons**: Requires credit card for verification

#### Steps:

1. **Create Railway Account**
   - Visit [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Create New Project**
   ```bash
   # Push code to GitHub first
   git add .
   git commit -m "Add JWT API service"
   git push
   ```

3. **Deploy JWT API**
   - Railway Dashboard → "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Set root directory: `jwt_api`
   - Railway auto-detects Python and installs dependencies

4. **Configure Environment**
   - Railway sets `PORT` automatically
   - No additional env vars needed

5. **Get API URL**
   - Railway provides: `https://your-app.railway.app`
   - Your JWT endpoint: `https://your-app.railway.app/api/token`

6. **Update Bot Configuration**
   ```bash
   # Set in Railway environment variables (for main bot service)
   JWT_API_URL=https://your-jwt-api.railway.app/api/token
   ```

---

### Option 2: Render

**Pros**: Free tier, no credit card required
**Cons**: Services sleep after 15 min of inactivity (free tier)

#### Steps:

1. **Create Render Account**
   - Visit [render.com](https://render.com)
   - Sign up with GitHub

2. **Create New Web Service**
   - Dashboard → "New" → "Web Service"
   - Connect GitHub repository
   - Root directory: `jwt_api`

3. **Configure Service**
   - **Name**: `freefire-jwt-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (2-3 minutes)

5. **Get API URL**
   - Render provides: `https://freefire-jwt-api.onrender.com`
   - Your JWT endpoint: `https://freefire-jwt-api.onrender.com/api/token`

6. **Update Bot**
   ```bash
   export JWT_API_URL=https://freefire-jwt-api.onrender.com/api/token
   ```

---

### Option 3: Fly.io

**Pros**: Good free tier, persistent apps
**Cons**: Requires CLI setup

#### Steps:

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**
   ```bash
   fly auth login
   ```

3. **Deploy**
   ```bash
   cd jwt_api
   fly launch --name freefire-jwt-api
   # Follow prompts, select region closest to your users
   ```

4. **Get URL**
   ```bash
   fly status
   # Shows: https://freefire-jwt-api.fly.dev
   ```

5. **Update Bot**
   ```bash
   export JWT_API_URL=https://freefire-jwt-api.fly.dev/api/token
   ```

---

### Option 4: Docker (Self-Hosted)

**Pros**: Full control, run anywhere
**Cons**: Requires server management

#### Steps:

1. **Build Image**
   ```bash
   cd jwt_api
   docker build -t freefire-jwt-api .
   ```

2. **Run Container**
   ```bash
   docker run -d \
     --name jwt-api \
     -p 3000:3000 \
     --restart unless-stopped \
     freefire-jwt-api
   ```

3. **Test**
   ```bash
   curl http://localhost:3000/health
   ```

4. **Update Bot**
   ```bash
   export JWT_API_URL=http://localhost:3000/api/token
   ```

---

### Option 5: Modal (Same as Bot)

**Pros**: Same platform as bot, unified deployment
**Cons**: Requires Modal account

#### Steps:

1. **Create Modal App**
   ```python
   # jwt_api_modal.py
   import modal

   app = modal.App("freefire-jwt-api")

   image = modal.Image.debian_slim().pip_install_from_requirements("requirements.txt")

   @app.function(image=image)
   @modal.web_endpoint(method="POST")
   async def generate_jwt(uid: str, password: str):
       from main import generate_token
       return await generate_token(uid, password)
   ```

2. **Deploy**
   ```bash
   modal deploy jwt_api_modal.py
   ```

3. **Get URL**
   - Modal provides endpoint URL
   - Update `JWT_API_URL` in bot

---

## 🧪 Testing Deployment

### 1. Health Check

```bash
curl https://your-jwt-api-url.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "freefire-jwt-api",
  "version": "1.0.0"
}
```

### 2. JWT Generation (GET)

```bash
curl "https://your-jwt-api-url.com/api/token?uid=YOUR_UID&password=YOUR_PASSWORD"
```

### 3. JWT Generation (POST)

```bash
curl -X POST https://your-jwt-api-url.com/api/token \
  -H "Content-Type: application/json" \
  -d '{"uid":"YOUR_UID","password":"YOUR_PASSWORD"}'
```

Expected response:
```json
{
  "token": "eyJ...",
  "lockRegion": "IND",
  "serverUrl": "https://client.ind.freefiremobile.com",
  "success": true,
  "message": "JWT token generated successfully"
}
```

### 4. Run Test Suite

```bash
# Set JWT_API_URL first
export JWT_API_URL=https://your-jwt-api-url.com/api/token

# Run tests
python test_jwt_api.py
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `PORT` | Server port | No | 3000 |
| `JWT_API_URL` | JWT API endpoint (for bot) | Yes | - |

### Bot Integration

Update `freefire/get_jwt_kaifcodec.py`:

```python
JWT_API_ENDPOINTS = [
    os.getenv("JWT_API_URL", ""),
    "http://localhost:3000/api/token",
    # Add your deployed URL here as fallback
    "https://your-jwt-api.railway.app/api/token",
]
```

---

## 📊 Monitoring

### Railway
- Dashboard → Service → Logs
- Real-time log streaming
- CPU/Memory metrics

### Render
- Dashboard → Service → Logs
- View recent logs
- Health check status

### Fly.io
```bash
fly logs
fly status
fly ssh console
```

### Docker
```bash
docker logs jwt-api -f
docker stats jwt-api
```

---

## 🐛 Troubleshooting

### Issue: API returns 500 error

**Symptoms**:
```json
{"detail":"Failed to generate JWT token"}
```

**Solutions**:
1. Check guest account credentials are valid
2. Verify OAuth endpoint is accessible
3. Check logs for detailed error

### Issue: API returns 401 error

**Symptoms**:
```json
{"detail":"Failed to authenticate with Garena OAuth"}
```

**Solutions**:
1. Verify guest UID/password are correct
2. Check if account is banned
3. Try with a different guest account

### Issue: Timeout errors

**Symptoms**:
```
httpx.TimeoutException
```

**Solutions**:
1. Increase timeout in client
2. Check network connectivity
3. Verify JWT API is running

### Issue: Import errors

**Symptoms**:
```
ModuleNotFoundError: No module named 'freefire'
```

**Solutions**:
1. Ensure protobuf files are copied to Docker image
2. Check Dockerfile COPY commands
3. Verify directory structure in deployment

---

## 🔒 Security

### Best Practices

1. **Don't commit secrets**
   - Use environment variables
   - Never hardcode guest credentials

2. **Rate limiting**
   - Consider adding rate limiting to API
   - Prevent abuse

3. **HTTPS only**
   - All platforms provide HTTPS by default
   - Never expose over HTTP in production

4. **Monitor logs**
   - Watch for suspicious activity
   - Track failed authentication attempts

### Recommended: Add API Key

Update `jwt_api/main.py`:

```python
from fastapi import Header, HTTPException

API_KEY = os.getenv("API_KEY", "")

@app.post("/api/token")
async def get_token_post(
    request: TokenRequest,
    x_api_key: str = Header(None)
):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return await generate_token(request.uid, request.password)
```

Then set `API_KEY` in environment and update bot to send it:

```python
headers = {"X-API-Key": os.getenv("API_KEY")}
response = await client.post(endpoint, json={...}, headers=headers)
```

---

## 📈 Scaling

### If You Need More Performance

1. **Increase replicas** (Railway/Render)
   - Scale horizontally
   - Load balancing automatic

2. **Add caching**
   - Cache JWT tokens (valid for ~1 hour)
   - Reduce OAuth calls

3. **Use Redis**
   - Cache successful JWT generations
   - Share cache across instances

4. **Optimize protobuf**
   - Pre-compile protobuf definitions
   - Reuse cipher objects

---

## 💰 Cost Estimates

### Railway
- Free: 500 hours/month
- Pro: $5/month (includes $5 credit)
- **JWT API**: ~$2-3/month

### Render
- Free: Spins down after 15 min inactivity
- Starter: $7/month (always on)
- **JWT API**: Free tier works well

### Fly.io
- Free: 3 shared-cpu VMs
- **JWT API**: Free tier sufficient

### Self-Hosted
- VPS: $5-10/month (Digital Ocean, Linode)
- Docker on existing server: $0

---

## 🎓 Next Steps

After deploying JWT API:

1. ✅ **Test JWT generation** with `test_jwt_api.py`
2. 🔗 **Update bot** with `JWT_API_URL`
3. 🧪 **Test likes flow** end-to-end
4. 📧 **Contact kaifcodec** for bulk accounts (see CONTACT_KAIFCODEC.md)
5. 📈 **Scale up** guest account pool

---

## 🆘 Support

### Resources
- **kaifcodec's Repo**: [freefire-jwt-generator-api](https://github.com/kaifcodec/freefire-jwt-generator-api)
- **Issues**: [Your repo issues]
- **Contact**: See CONTACT_KAIFCODEC.md

### Community
- Telegram: [Your support group]
- Discord: [Your server]
- Email: [Your email]

---

**Last Updated**: 2025-01-15
**Version**: 1.0.0
**Based on**: kaifcodec's freefire-jwt-generator-api
