# Quick Deploy: JWT API

## 🚀 5-Minute Deployment Guide

### Prerequisites
- ✅ Code pushed to GitHub
- ✅ Railway or Render account
- ✅ Guest accounts in `freefire/guests_manager/guests_converted.json`

---

## Option 1: Railway (Easiest)

### Step 1: Deploy
1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Click "Add Service" → "New Service"
6. Set root directory: `jwt_api`
7. Wait 2-3 minutes for deployment

### Step 2: Get URL
- Railway provides: `https://your-app-name.railway.app`
- Your JWT endpoint: `https://your-app-name.railway.app/api/token`

### Step 3: Configure Bot
1. In Railway, go to your main bot service
2. Add environment variable:
   ```
   JWT_API_URL=https://your-jwt-api.railway.app/api/token
   ```
3. Redeploy bot (Railway does this automatically)

### Step 4: Test
```bash
curl https://your-jwt-api.railway.app/health
```

---

## Option 2: Render (Free)

### Step 1: Deploy
1. Go to [render.com](https://render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `freefire-jwt-api`
   - **Root Directory**: `jwt_api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Click "Create Web Service"
6. Wait 3-5 minutes for deployment

### Step 2: Get URL
- Render provides: `https://freefire-jwt-api.onrender.com`
- Your JWT endpoint: `https://freefire-jwt-api.onrender.com/api/token`

### Step 3: Configure Bot
Add to your bot's environment:
```
JWT_API_URL=https://freefire-jwt-api.onrender.com/api/token
```

### Step 4: Test
```bash
curl https://freefire-jwt-api.onrender.com/health
```

---

## Option 3: Local Testing

### Step 1: Install
```bash
cd jwt_api
pip install -r requirements.txt
```

### Step 2: Run
```bash
uvicorn main:app --host 0.0.0.0 --port 3000
```

### Step 3: Configure Bot
```bash
export JWT_API_URL=http://localhost:3000/api/token
```

### Step 4: Test
```bash
curl http://localhost:3000/health
```

---

## 🧪 Verify Deployment

### Test 1: Health Check
```bash
curl https://your-jwt-api-url.com/health
```

**Expected**:
```json
{
  "status": "healthy",
  "service": "freefire-jwt-api",
  "version": "1.0.0"
}
```

### Test 2: JWT Generation
```bash
# Get a guest account from your file
cat freefire/guests_manager/guests_converted.json | head -20

# Test JWT generation
curl -X POST https://your-jwt-api-url.com/api/token \
  -H "Content-Type: application/json" \
  -d '{"uid":"YOUR_UID","password":"YOUR_PASSWORD"}'
```

**Expected**:
```json
{
  "token": "eyJ...",
  "lockRegion": "IND",
  "serverUrl": "https://client.ind.freefiremobile.com",
  "success": true
}
```

### Test 3: Run Test Suite
```bash
# Set your JWT API URL
export JWT_API_URL=https://your-jwt-api-url.com/api/token

# Run tests
python test_jwt_api.py
```

**Expected**:
```
✅ All critical tests passed! ✨
```

---

## 🐛 Common Issues

### Issue: "Service failed to start"

**Railway**:
- Check logs in Railway dashboard
- Verify `jwt_api` directory exists
- Ensure `requirements.txt` is present

**Render**:
- Check build logs
- Verify Python version (should use 3.11+)
- Check start command is correct

**Fix**:
```bash
# Verify files exist
ls jwt_api/
# Should show: main.py, requirements.txt, Dockerfile, etc.
```

### Issue: "Module not found: freefire"

**Cause**: Protobuf files not copied to deployment

**Railway/Render Fix**:
Update Dockerfile:
```dockerfile
# Copy protobuf files
COPY ../freefire/ff_proto /app/freefire/ff_proto
COPY ../freefire/__init__.py /app/freefire/
```

**Local Fix**:
```bash
# Run from project root, not jwt_api directory
cd ..
export PYTHONPATH=$PYTHONPATH:$(pwd)
cd jwt_api
uvicorn main:app --port 3000
```

### Issue: "Failed to get OAuth token"

**Cause**: Invalid guest credentials

**Fix**:
1. Verify guest account credentials are correct
2. Test with different guest account
3. Check if account is banned

```bash
# Test with first account in file
python -c "
import json
with open('freefire/guests_manager/guests_converted.json') as f:
    account = json.load(f)[0]
    print(f\"UID: {account['uid']}\")
    print(f\"Password: {account['password']}\")
"
```

---

## 📊 Monitoring

### Railway
- **Logs**: Dashboard → Service → Logs tab
- **Metrics**: Dashboard → Service → Metrics tab
- **URL**: Dashboard → Service → Deployments tab

### Render
- **Logs**: Dashboard → Service → Logs
- **Health**: Dashboard → Service → Info
- **URL**: Shown at top of service page

### Local
```bash
# View logs
tail -f /tmp/jwt-api.log

# Check process
ps aux | grep uvicorn

# Test health
watch -n 5 curl http://localhost:3000/health
```

---

## 💰 Cost

### Railway
- **Free Tier**: 500 hours/month (~21 days)
- **Hobby**: $5/month (includes $5 credit)
- **JWT API usage**: ~$2-3/month

### Render
- **Free Tier**: Unlimited (spins down after 15 min)
- **Starter**: $7/month (always on)
- **JWT API usage**: Free tier works fine

### Local
- **Cost**: $0
- **Requirements**: Server with public IP
- **Alternative**: Use ngrok for testing

---

## ✅ Success Checklist

- [ ] JWT API deployed to Railway/Render
- [ ] Health check returns 200 OK
- [ ] JWT generation works with test account
- [ ] `JWT_API_URL` set in bot environment
- [ ] Bot redeployed with new config
- [ ] Test suite passes (`python test_jwt_api.py`)
- [ ] End-to-end likes test works

---

## 🎯 Next Steps After Deployment

1. **Test Likes Flow**
   ```bash
   # In Telegram, send to your bot
   /like YOUR_UID 5
   ```

2. **Monitor Logs**
   - Watch for JWT generation logs
   - Check for errors
   - Verify success rate

3. **Contact kaifcodec**
   - See `CONTACT_KAIFCODEC.md`
   - Request bulk guest accounts
   - Share your experience

4. **Scale Up**
   - Add more guest accounts
   - Monitor usage patterns
   - Optimize as needed

---

## 📚 Full Documentation

- **Deployment**: `JWT_API_DEPLOYMENT.md` (comprehensive guide)
- **Implementation**: `KAIFCODEC_JWT_IMPLEMENTATION.md` (technical details)
- **Contact**: `CONTACT_KAIFCODEC.md` (bulk accounts)
- **API Docs**: `jwt_api/README.md` (API reference)

---

## 🆘 Need Help?

### Quick Fixes
1. Check logs (Railway/Render dashboard)
2. Verify environment variables
3. Test with `curl` commands above
4. Run `python test_jwt_api.py`

### Documentation
- Read `JWT_API_DEPLOYMENT.md` for detailed troubleshooting
- Check `jwt_api/README.md` for API details

### Community
- GitHub Issues: [Your repo issues]
- Email: [Your support email]
- Based on: [kaifcodec/freefire-jwt-generator-api](https://github.com/kaifcodec/freefire-jwt-generator-api)

---

**Estimated Time**: 5-10 minutes
**Difficulty**: Easy
**Cost**: Free (Render) or $2-3/month (Railway)

**Last Updated**: 2025-01-15
