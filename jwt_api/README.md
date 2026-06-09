# Free Fire JWT Generator API

A FastAPI service for generating Free Fire JWT tokens from guest account credentials.

**Based on**: [kaifcodec/freefire-jwt-generator-api](https://github.com/kaifcodec/freefire-jwt-generator-api)

---

## 🎯 What It Does

This API transforms Free Fire guest account credentials into valid JWT tokens that can be used for API authentication:

1. **OAuth Token**: Gets OAuth access token from Garena servers
2. **Protobuf Encoding**: Creates LoginReq protobuf message
3. **AES Encryption**: Encrypts with Free Fire's encryption keys
4. **JWT Token**: Returns ready-to-use JWT

---

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn main:app --host 0.0.0.0 --port 3000

# Test
curl http://localhost:3000/health
```

### Docker

```bash
# Build
docker build -t freefire-jwt-api .

# Run
docker run -p 3000:3000 freefire-jwt-api
```

---

## 📡 API Endpoints

### Health Check
```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "freefire-jwt-api",
  "version": "1.0.0"
}
```

### Generate JWT (GET)
```
GET /api/token?uid=YOUR_UID&password=YOUR_PASSWORD
```

### Generate JWT (POST)
```
POST /api/token
Content-Type: application/json

{
  "uid": "1234567890",
  "password": "your_password"
}
```

Response:
```json
{
  "token": "eyJhbGciOiJI...",
  "lockRegion": "IND",
  "serverUrl": "https://client.ind.freefiremobile.com",
  "success": true,
  "message": "JWT token generated successfully"
}
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | 3000 |

### Constants (in main.py)

- `MAIN_KEY`: AES encryption key (Base64)
- `MAIN_IV`: AES initialization vector (Base64)
- `OAUTH_URL`: Garena OAuth endpoint
- `USER_AGENT`: Android user agent string

---

## 📦 Dependencies

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
httpx==0.27.2
protobuf==6.30.0
pycryptodome==3.20.0
pydantic==2.9.2
```

---

## 🏗️ Architecture

```
┌─────────────┐
│   Client    │
│   (Bot)     │
└──────┬──────┘
       │ POST /api/token
       │ {uid, password}
       ▼
┌──────────────────┐
│   JWT API        │
│   FastAPI        │
└──────┬───────────┘
       │
       ├─► Step 1: OAuth Token
       │   https://ffmconnect.live.gop.garenanow.com
       │
       ├─► Step 2: Protobuf Message
       │   LoginReq(open_id, login_token)
       │
       ├─► Step 3: AES Encryption
       │   AES-128-CBC
       │
       └─► Step 4: Return JWT
           Base64 encoded token
```

---

## 🔐 Security

### Encryption Details

- **Algorithm**: AES-128-CBC
- **Key**: 16 bytes (extracted from Free Fire client)
- **IV**: 16 bytes (extracted from Free Fire client)
- **Padding**: PKCS7

### OAuth Flow

1. Client sends UID/password to JWT API
2. JWT API requests OAuth token from Garena
3. Garena validates credentials and returns access_token
4. JWT API transforms access_token to JWT format
5. JWT returned to client

### Best Practices

- Never log JWT tokens in production
- Use HTTPS for all API calls
- Rate limit requests to prevent abuse
- Monitor for failed authentication attempts

---

## 🧪 Testing

### Manual Testing

```bash
# Test with real guest account
curl -X POST http://localhost:3000/api/token \
  -H "Content-Type: application/json" \
  -d '{"uid":"YOUR_UID","password":"YOUR_PASSWORD"}'
```

### Automated Testing

```bash
# From project root
python test_jwt_api.py
```

---

## 📚 Documentation

- **Full Deployment Guide**: See `../JWT_API_DEPLOYMENT.md`
- **Bot Integration**: See `../freefire/get_jwt_kaifcodec.py`
- **Testing**: See `../test_jwt_api.py`

---

## 🐛 Troubleshooting

### Issue: "Failed to get OAuth token"

**Cause**: Invalid credentials or Garena server issues

**Solutions**:
- Verify UID/password are correct
- Check if account is banned
- Test with different guest account

### Issue: "Failed to generate JWT token"

**Cause**: Protobuf or encryption error

**Solutions**:
- Check protobuf files are present
- Verify pycryptodome is installed
- Check logs for detailed error

### Issue: Import errors

**Cause**: Missing freefire module

**Solutions**:
- Ensure parent directory is in Python path
- For Docker: Verify COPY commands in Dockerfile

---

## 📈 Performance

### Benchmarks

- **Average Response Time**: 500-800ms
- **OAuth Call**: 400-600ms
- **JWT Generation**: 50-100ms
- **Concurrent Requests**: 50+ simultaneous

### Optimization Tips

1. **Caching**: Cache JWT tokens (valid for ~1 hour)
2. **Connection Pooling**: Reuse HTTP connections
3. **Async**: Use async/await throughout
4. **Protobuf**: Pre-compile protobuf definitions

---

## 🚀 Deployment

### Railway
```bash
git push
# Railway auto-deploys
```

### Render
```bash
# Connect GitHub repo in dashboard
# Render auto-deploys on push
```

### Fly.io
```bash
fly launch
fly deploy
```

See `../JWT_API_DEPLOYMENT.md` for detailed instructions.

---

## 🙏 Credits

This implementation is based on **kaifcodec's** excellent work:

- **Original Repository**: [kaifcodec/freefire-jwt-generator-api](https://github.com/kaifcodec/freefire-jwt-generator-api)
- **Author**: kaifcodec
- **Email**: kaifcodec@gmail.com

### What We Changed

- Adapted for FastAPI
- Added fallback mechanisms
- Integrated with existing protobuf definitions
- Added comprehensive error handling
- Created deployment configurations

---

## 📄 License

**Protective Source License v1.0 (PSL-1.0)**

Copyright (c) 2025 kaifcodec

This code is provided for legitimate Free Fire development purposes only.
Unauthorized removal of credits or use for abusive/illegal purposes will
terminate all rights granted under this license.

---

## 🔗 Links

- **Main Bot**: `../bot.py`
- **Client Code**: `../freefire/get_jwt_kaifcodec.py`
- **Test Suite**: `../test_jwt_api.py`
- **Deployment Guide**: `../JWT_API_DEPLOYMENT.md`
- **Contact Info**: `../CONTACT_KAIFCODEC.md`

---

**Version**: 1.0.0
**Last Updated**: 2025-01-15
