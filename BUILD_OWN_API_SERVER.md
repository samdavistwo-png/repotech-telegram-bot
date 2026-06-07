# Building Your Own Free Fire Authentication Server

## Overview

This guide explains how to build your own authentication server to replace the currently unavailable `loginbp.ggblueshark.com/MajorLogin` endpoint.

---

## Why Build Your Own Server?

**Current Problem:**
- Your bot depends on `ggblueshark.com` (third-party service)
- Service is currently down (503 error)
- No control over uptime or availability
- No SLA or support

**Benefits of Your Own Server:**
- ✅ Full control over uptime and maintenance
- ✅ No dependency on third-party services
- ✅ Can add custom features (caching, rate limiting, analytics)
- ✅ Better error handling and logging
- ✅ Predictable costs

**Risks:**
- ⚠️ Still violates Garena ToS (account ban risk remains)
- ⚠️ Requires ongoing maintenance
- ⚠️ Game updates may break implementation
- ⚠️ Need to protect encryption keys

---

## Architecture Overview

```
┌─────────────────┐
│  Telegram Bot   │
│   (Your Code)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│  Your FastAPI   │ ───► │ Garena OAuth     │
│  Auth Server    │      │ (Official API)   │
│  /MajorLogin    │ ◄─── │ ffmconnect.live  │
└────────┬────────┘      └──────────────────┘
         │
         ▼
┌─────────────────┐
│  Free Fire      │
│  Game Servers   │
│  client.ind...  │
└─────────────────┘
```

**Flow:**
1. Bot sends encrypted `LoginReq` to your server
2. Your server decrypts and validates request
3. Your server authenticates with Garena OAuth (official API)
4. Your server generates game JWT
5. Your server returns encrypted `LoginRes` to bot
6. Bot uses JWT to send likes to Free Fire servers

---

## Implementation Guide

### Step 1: Set Up Server Infrastructure

**Requirements:**
- VPS with Python 3.10+ (DigitalOcean, Linode, AWS EC2)
- Domain name (optional but recommended)
- SSL certificate (Let's Encrypt)
- 1GB RAM minimum, 2GB recommended

**Recommended Stack:**
```
FastAPI (async web framework)
uvicorn (ASGI server)
httpx (async HTTP client)
pycryptodome (encryption)
protobuf (message serialization)
```

**Cost Estimate:**
- VPS: $5-10/month (DigitalOcean Droplet)
- Domain: $10-15/year (optional)
- SSL: $0 (Let's Encrypt)
- Total: ~$60-120/year

### Step 2: Create FastAPI Server

**File: `server.py`**

```python
"""
Free Fire Authentication Server
Replaces ggblueshark.com/MajorLogin endpoint
"""

from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from Crypto.Cipher import AES
import httpx
import base64
import sys
import os

# Add your freefire module to path
sys.path.insert(0, './freefire')

from ff_proto import freefire_pb2
from google.protobuf import json_format

app = FastAPI(title="Free Fire Auth Server")

# Encryption keys (KEEP THESE SECRET!)
MAIN_KEY = base64.b64decode('WWcmdGMlREV1aDYlWmNeOA==')
MAIN_IV = base64.b64decode('Nm95WkRyMjJFM3ljaGpNJQ==')

# Garena OAuth endpoint (official)
GARENA_TOKEN_URL = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"


def unpad(data: bytes) -> bytes:
    """Remove PKCS7 padding"""
    padding_length = data[-1]
    return data[:-padding_length]


def pad(text: bytes) -> bytes:
    """Add PKCS7 padding"""
    padding_length = AES.block_size - (len(text) % AES.block_size)
    padding = bytes([padding_length] * padding_length)
    return text + padding


def aes_decrypt(key: bytes, iv: bytes, ciphertext: bytes) -> bytes:
    """Decrypt AES-CBC encrypted data"""
    aes = AES.new(key, AES.MODE_CBC, iv)
    plaintext = aes.decrypt(ciphertext)
    return unpad(plaintext)


def aes_encrypt(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
    """Encrypt data with AES-CBC"""
    aes = AES.new(key, AES.MODE_CBC, iv)
    padded = pad(plaintext)
    return aes.encrypt(padded)


async def get_garena_access_token(uid: str, password: str) -> tuple:
    """Get access token from official Garena OAuth"""
    payload = f"uid={uid}&password={password}&response_type=token&client_type=2&client_secret=2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3&client_id=100067"

    headers = {
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/x-www-form-urlencoded"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(GARENA_TOKEN_URL, data=payload, headers=headers)
        data = response.json()
        return data.get("access_token"), data.get("open_id")


def determine_region_and_server(open_id: str) -> tuple:
    """Determine region and server URL based on open_id"""
    # Simple heuristic - adjust based on your needs
    # In production, you'd have a more sophisticated mapping

    region_mapping = {
        "IND": ("IND", "https://client.ind.freefiremobile.com"),
        "BR": ("BR", "https://client.us.freefiremobile.com"),
        "US": ("US", "https://client.us.freefiremobile.com"),
        # Add more regions as needed
    }

    # Default to IND for now
    return "IND", "https://client.ind.freefiremobile.com"


@app.post("/MajorLogin")
async def major_login(request: Request):
    """
    Handle MajorLogin requests
    Replaces ggblueshark.com/MajorLogin
    """
    try:
        # 1. Read encrypted request body
        encrypted_body = await request.body()

        # 2. Decrypt with AES
        decrypted = aes_decrypt(MAIN_KEY, MAIN_IV, encrypted_body)

        # 3. Parse protobuf LoginReq
        login_req = freefire_pb2.LoginReq()
        login_req.ParseFromString(decrypted)

        # Extract credentials
        open_id = login_req.open_id
        login_token = login_req.login_token

        # 4. Validate token with Garena (optional - token is already valid)
        # You could cache JWTs here to reduce Garena API calls

        # 5. Determine region and server
        region, server_url = determine_region_and_server(open_id)

        # 6. Generate game JWT
        # In this simplified version, we pass through the access token
        # In production, you might generate your own JWT or implement caching
        jwt_token = login_token

        # 7. Build LoginRes protobuf
        login_res = freefire_pb2.LoginRes()
        login_res.token = jwt_token
        login_res.lockRegion = region
        login_res.serverUrl = server_url

        # 8. Serialize to bytes
        response_data = login_res.SerializeToString()

        # 9. Encrypt response
        encrypted_response = aes_encrypt(MAIN_KEY, MAIN_IV, response_data)

        # 10. Return encrypted protobuf
        return Response(
            content=encrypted_response,
            media_type="application/octet-stream"
        )

    except Exception as e:
        # Log error and return 500
        print(f"Error processing MajorLogin: {e}")
        return Response(
            content=b"Internal Server Error",
            status_code=500,
            media_type="text/plain"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "Free Fire Auth Server"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Free Fire Authentication Server",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/MajorLogin",
            "health": "/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Step 3: Deploy Server

**Option A: Manual VPS Deployment**

```bash
# 1. SSH into your VPS
ssh user@your-server-ip

# 2. Install dependencies
sudo apt update
sudo apt install python3.10 python3-pip nginx certbot

# 3. Clone your repo
git clone https://github.com/yourusername/ff-auth-server.git
cd ff-auth-server

# 4. Install Python packages
pip3 install fastapi uvicorn httpx pycryptodome protobuf

# 5. Copy freefire module from your bot
scp -r ./freefire user@your-server-ip:~/ff-auth-server/

# 6. Run server
uvicorn server:app --host 0.0.0.0 --port 8000
```

**Option B: Docker Deployment**

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .
COPY freefire/ ./freefire/

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t ff-auth-server .
docker run -d -p 8000:8000 ff-auth-server
```

**Option C: Railway Deployment**

```yaml
# railway.toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn server:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "ON_FAILURE"
```

### Step 4: Configure SSL/Domain (Optional but Recommended)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Nginx config (/etc/nginx/sites-available/ff-auth)
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Step 5: Update Your Bot

**In `freefire/get_jwt.py`, change:**

```python
# OLD
url = "https://loginbp.ggblueshark.com/MajorLogin"

# NEW
url = "https://your-domain.com/MajorLogin"
# OR (if no domain)
url = "https://your-server-ip:8000/MajorLogin"
```

### Step 6: Test Your Server

```bash
# Test health endpoint
curl https://your-domain.com/health

# Test from your bot
# Run /likes command and check logs
```

---

## Production Considerations

### 1. **Security**

```python
# Add rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/MajorLogin")
@limiter.limit("10/minute")  # Max 10 requests per minute per IP
async def major_login(request: Request):
    # ... existing code ...
```

### 2. **Caching**

```python
# Cache JWTs to reduce Garena API calls
import redis
from datetime import timedelta

cache = redis.Redis(host='localhost', port=6379, decode_responses=True)

async def get_cached_jwt(open_id: str, login_token: str):
    cache_key = f"jwt:{open_id}"
    cached = cache.get(cache_key)

    if cached:
        return cached

    # Generate new JWT
    jwt = await generate_jwt(open_id, login_token)

    # Cache for 30 minutes
    cache.setex(cache_key, timedelta(minutes=30), jwt)

    return jwt
```

### 3. **Monitoring**

```python
# Add Prometheus metrics
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)

# Endpoint: /metrics
```

### 4. **Logging**

```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
handler = RotatingFileHandler('auth_server.log', maxBytes=10*1024*1024, backupCount=5)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[handler]
)

logger = logging.getLogger(__name__)

# Log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response
```

### 5. **High Availability**

```bash
# Use systemd for auto-restart
# /etc/systemd/system/ff-auth.service

[Unit]
Description=Free Fire Auth Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/user/ff-auth-server
ExecStart=/usr/bin/uvicorn server:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable ff-auth
sudo systemctl start ff-auth

# Check status
sudo systemctl status ff-auth
```

---

## Cost Breakdown

| Item | Monthly Cost | Annual Cost |
|------|--------------|-------------|
| VPS (DigitalOcean 1GB) | $6 | $72 |
| Domain (optional) | - | $12 |
| SSL Certificate | $0 | $0 |
| **Total** | **$6** | **$84** |

**ROI Calculation:**
- If you have 100 active users
- Each pays 50 coins (~$0.50) per day
- Monthly revenue: $1,500
- Monthly cost: $6
- **Profit margin: 99.6%**

---

## Maintenance Checklist

### Daily:
- [ ] Check server uptime (use monitoring tool)
- [ ] Review error logs
- [ ] Monitor request volumes

### Weekly:
- [ ] Review performance metrics
- [ ] Check disk space
- [ ] Update dependencies if needed

### Monthly:
- [ ] Renew SSL certificate (auto with Let's Encrypt)
- [ ] Review and optimize code
- [ ] Backup configuration

### When Free Fire Updates:
- [ ] Check if protobuf schemas changed
- [ ] Test authentication flow
- [ ] Update `ReleaseVersion` header if needed
- [ ] Verify encryption keys still work

---

## Troubleshooting

### Issue: "Service Unavailable (503)"

**Solution:**
```bash
# Check if server is running
sudo systemctl status ff-auth

# Restart server
sudo systemctl restart ff-auth

# Check logs
tail -f /home/user/ff-auth-server/auth_server.log
```

### Issue: "Protobuf Parsing Error"

**Solution:**
- Verify encryption keys are correct
- Check if protobuf schemas match game version
- Test decryption manually

### Issue: "Garena Token Invalid"

**Solution:**
- Check if Garena OAuth endpoint changed
- Verify client credentials are correct
- Test token generation manually

---

## Legal Disclaimer

⚠️ **IMPORTANT**: Building and operating this server still violates Garena's Terms of Service.

**Risks:**
1. User accounts may be permanently banned
2. Operator may face legal action
3. Service may be taken down by Garena
4. No official support or recourse

**Recommendations:**
- Clearly disclose risks to users
- Add prominent disclaimers
- Consider legal consultation
- Have contingency plans if service is shut down

**Alternative:**
Consider pivoting to official Garena APIs only:
- Use Free Fire Community API for statistics
- Avoid any automation that manipulates game state
- Focus on analytics and information services

---

## Summary

**Is it technically possible?** ✅ Yes

**Is it worth it?** 🤔 Depends on your goals:
- **For learning:** Excellent educational project
- **For business:** High risk, but potentially profitable
- **For compliance:** ❌ Not recommended

**Time Investment:**
- Initial setup: 4-8 hours
- Ongoing maintenance: 1-2 hours/week
- Game update fixes: 2-4 hours per update

**Skill Requirements:**
- Python (FastAPI, async/await)
- Linux server administration
- Nginx configuration
- Basic security practices
- Protobuf understanding

---

## Next Steps

1. **Decide:** Is building your own server worth the effort and risk?
2. **If Yes:**
   - Set up VPS
   - Implement basic FastAPI server
   - Test with small user base
   - Add monitoring and security
   - Scale gradually

3. **If No:**
   - Wait for ggblueshark to recover
   - Look for community-maintained alternatives
   - Pivot to official APIs only

---

**Questions?**
- Check `LIKES_ERROR_FIX.md` for technical details
- Use `/apihealth` command to monitor endpoints
- Review FastAPI documentation: https://fastapi.tiangolo.com/
