# RepotechBot - 24/7 Deployment Guide

**Last Updated:** June 6, 2026
**Bot:** RepotechBot
**Features:** Full coin economy + Free Fire likes (161 guest accounts)

---

## ✅ Best Hosting Platforms for 24/7 Operation

### Recommended: Railway (Easiest for 24/7)

**Why Railway:**
- ✅ Free tier with 500 hours/month
- ✅ Automatic SSL
- ✅ Environment variable management
- ✅ One-click deploy from GitHub
- ✅ Always-on (doesn't sleep)
- ✅ SQLite database persists

**Deployment Steps:**

1. **Sign up at Railway.app**
   - Go to https://railway.app
   - Sign in with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `samdavistwo-png/repotech-telegram-bot`
   - Branch: `main` (after PR is merged)

3. **Configure Environment Variables**
   ```
   BOT_TOKEN=8963786165:AAGDcSbQxbv7sGUfrJK95TpeT-u7nJMO2ps
   ADMIN_ID=YOUR_TELEGRAM_USER_ID
   UPI_ID=rsamofflceprv.ldt@fam
   PYTHONUNBUFFERED=1
   ```

4. **Set Start Command**
   - Railway auto-detects Python
   - Start command: `python bot.py`

5. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes
   - Bot will start automatically

6. **Configure Keep-Alive**
   - Railway provides a public URL
   - Use UptimeRobot to ping: `https://your-app.up.railway.app`
   - Interval: Every 5 minutes

**Cost:** Free (500 hours/month = 20 days continuous)

---

### Alternative 1: Render

**Why Render:**
- ✅ Completely free tier
- ✅ Automatic deployments from GitHub
- ✅ Environment variables
- ❌ Free tier sleeps after 15 minutes inactivity
- ✅ Wake-up via Keep-Alive pings

**Important:** Free tier sleeps! You MUST configure UptimeRobot.

**Deployment Steps:**

1. **Sign up at Render.com**
   - Go to https://render.com
   - Sign in with GitHub

2. **Create Web Service**
   - Dashboard → "New +"
   - Select "Web Service"
   - Connect GitHub repo: `repotech-telegram-bot`

3. **Configure Service**
   ```
   Name: repotech-telegram-bot
   Region: Choose closest to India (for Free Fire)
   Branch: main
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python bot.py
   ```

4. **Environment Variables**
   ```
   BOT_TOKEN=8963786165:AAGDcSbQxbv7sGUfrJK95TpeT-u7nJMO2ps
   ADMIN_ID=YOUR_TELEGRAM_USER_ID
   UPI_ID=rsamofflceprv.ldt@fam
   PYTHON_VERSION=3.9
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait 5-10 minutes for first deploy

6. **Configure Keep-Alive (CRITICAL for free tier)**
   - Note your Render URL: `https://repotech-telegram-bot.onrender.com`
   - Set up UptimeRobot (see below)

**Cost:** Free (but sleeps without pings)

---

### Alternative 2: Fly.io

**Why Fly.io:**
- ✅ Free tier with always-on capability
- ✅ Multiple regions (choose closest to India)
- ✅ Good for global users
- ❌ Requires CLI setup (more technical)

**Deployment Steps:**

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**
   ```bash
   fly auth login
   ```

3. **Initialize App**
   ```bash
   cd repotech-telegram-bot
   fly launch
   ```

   Answer prompts:
   - App name: `repotech-bot`
   - Region: `sin` (Singapore - closest to India)
   - PostgreSQL: No
   - Redis: No

4. **Set Secrets**
   ```bash
   fly secrets set BOT_TOKEN="8963786165:AAGDcSbQxbv7sGUfrJK95TpeT-u7nJMO2ps"
   fly secrets set ADMIN_ID="YOUR_TELEGRAM_USER_ID"
   fly secrets set UPI_ID="rsamofflceprv.ldt@fam"
   ```

5. **Deploy**
   ```bash
   fly deploy
   ```

6. **Scale to Always-On**
   ```bash
   fly scale count 1
   ```

**Cost:** Free (with limits)

---

## ⚙️ Keep-Alive Configuration (CRITICAL)

For platforms that sleep (Render, Heroku), you MUST configure uptime monitoring.

### UptimeRobot Setup (Free)

1. **Sign up at UptimeRobot.com**
   - Go to https://uptimerobot.com
   - Create free account

2. **Create New Monitor**
   - Dashboard → "Add New Monitor"
   - Monitor Type: HTTP(s)
   - Friendly Name: RepotechBot Keep-Alive
   - URL: `https://your-app-url:8080/` (or your hosting URL)
   - Monitoring Interval: 5 minutes

3. **Save Monitor**
   - UptimeRobot will ping every 5 minutes
   - Keeps your bot awake 24/7

**Alternative Services:**
- BetterUptime (free)
- Pingdom (paid)
- StatusCake (free tier)

---

## 🔧 Environment Configuration

### Required Environment Variables

```env
# Telegram Bot Token from @BotFather
BOT_TOKEN=8963786165:AAGDcSbQxbv7sGUfrJK95TpeT-u7nJMO2ps

# Your Telegram User ID (get from @userinfobot)
ADMIN_ID=123456789  # ⚠️ REPLACE THIS

# UPI ID for payments
UPI_ID=rsamofflceprv.ldt@fam
```

### Getting Your Admin ID

1. Open Telegram
2. Search for `@userinfobot`
3. Start the bot
4. Copy the number shown as "Id"
5. Use that number as `ADMIN_ID`

---

## 🎯 Free Fire Likes - How It Works 24/7

### Current Implementation

Your bot has **161 Indian Free Fire guest accounts** ready to send likes.

**How it works:**
1. User sends `/likes 123456789` (their Free Fire UID)
2. Bot deducts 50 coins
3. Bot uses 100 guest accounts to send 1 like each = 100 total likes
4. Likes are sent concurrently (20 at a time for speed)
5. Bot verifies likes were added

### Important Notes

**Guest Account Pool:**
- You have 161 accounts in `freefire/guests_manager/guests_converted.json`
- Each account can send likes multiple times
- Accounts are from India (IND server only)

**Limits:**
- Each user: 3 requests per day (300 likes max per day per user)
- Each request sends: 100 likes
- Cost: 50 coins per 100 likes

**24/7 Operation:**
- Bot automatically handles all requests
- No manual intervention needed
- Guest accounts rotate automatically
- Concurrent sending ensures speed

### If Guest Accounts Stop Working

Guest accounts may expire over time. Here's how to handle it:

**Option 1: Get New Guest Accounts**
- Source new Free Fire guest accounts (JSON format)
- Replace `freefire/guests_manager/guests_converted.json`
- Restart bot

**Option 2: Monitor & Alert**
- Check bot logs for Free Fire API errors
- Add admin notification when likes fail
- Replenish guest accounts as needed

---

## 📊 Monitoring Your 24/7 Bot

### Check Bot Status

1. **Send `/start` to your bot**
   - Should respond immediately
   - If no response, bot is down

2. **Check Hosting Platform Logs**
   - Railway: Dashboard → Deployments → Logs
   - Render: Dashboard → Logs tab
   - Fly.io: `fly logs`

3. **Admin Commands**
   - `/stats` - View bot statistics
   - `/allusers` - See all registered users
   - Shows uptime and activity

### Set Up Alerts

**UptimeRobot Alerts (Free):**
- Email when bot goes down
- SMS alerts (paid plan)
- Webhook notifications

**Hosting Platform Alerts:**
- Railway: Built-in email alerts
- Render: Email on deployment failures
- Fly.io: Email on crashes

---

## 🔄 Automatic Deployments

### GitHub Auto-Deploy

Most platforms support automatic deployment when you push to GitHub:

**Railway:**
- Automatically deploys on push to `main`
- No configuration needed

**Render:**
- Auto-deploys on push to `main`
- Enable "Auto-Deploy" in settings

**Fly.io:**
- Set up GitHub Actions:
  ```yaml
  # .github/workflows/fly.yml
  name: Fly Deploy
  on:
    push:
      branches: [main]
  jobs:
    deploy:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v2
        - uses: superfly/flyctl-actions/setup-flyctl@master
        - run: flyctl deploy --remote-only
          env:
            FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
  ```

---

## 🛡️ Database Backup (Important!)

Your bot uses SQLite database: `repotech_bot.db`

**Why Backup:**
- User balances
- Transaction history
- Free Fire usage records
- Redeem keys
- Payment records

### Automatic Backup Options

**Option 1: GitHub Actions (Free)**
```yaml
# .github/workflows/backup.yml
name: Daily DB Backup
on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight
jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - name: Backup DB
        run: |
          # Download DB from hosting platform
          # Upload to GitHub Releases or S3
```

**Option 2: Railway Volumes**
- Railway persists data automatically
- Database survives redeployments

**Option 3: Manual Backups**
```bash
# Download from hosting platform
railway run sqlite3 repotech_bot.db ".backup backup.db"

# Or via SSH/console
sqlite3 repotech_bot.db ".backup /tmp/backup-$(date +%Y%m%d).db"
```

---

## 🚀 Quick Start Checklist

### Pre-Deployment
- [ ] Get your Telegram User ID from @userinfobot
- [ ] Choose hosting platform (Railway recommended)
- [ ] Merge PR #2 to main branch

### Deployment
- [ ] Sign up for hosting platform
- [ ] Create new project from GitHub
- [ ] Set environment variables (BOT_TOKEN, ADMIN_ID, UPI_ID)
- [ ] Deploy and wait for build

### Post-Deployment
- [ ] Test bot with `/start` command
- [ ] Set up UptimeRobot monitoring (if using Render/Heroku)
- [ ] Test admin commands (`/admin`, `/stats`)
- [ ] Test Free Fire likes with real UID
- [ ] Configure database backups

### 24/7 Verification
- [ ] Bot responds within 5 seconds
- [ ] UptimeRobot shows "Up" status
- [ ] Keep-Alive endpoint returns 200 OK
- [ ] Free Fire likes working
- [ ] No crashes in logs

---

## 🆘 Troubleshooting 24/7 Operation

### Bot Not Responding

**Check 1: Is it running?**
```bash
# Railway
railway logs

# Render
# Check Logs tab in dashboard

# Fly.io
fly status
fly logs
```

**Check 2: Environment variables set?**
- Verify BOT_TOKEN is correct
- Verify ADMIN_ID is your user ID
- Check for typos

**Check 3: Platform sleeping?**
- Is UptimeRobot configured?
- Check last ping time
- Verify Keep-Alive URL is correct

### Free Fire Likes Not Working

**Check 1: Guest accounts valid?**
```python
# Test one guest account manually
python freefire/send_like.py
```

**Check 2: User has enough coins?**
- Each request costs 50 coins
- Check with `/balance`

**Check 3: Daily limit reached?**
- Each user: 3 requests per day
- Check with `/likestatus`

**Check 4: Logs for errors**
```bash
# Look for Free Fire API errors
railway logs | grep "Free Fire"
```

### Database Lost

**If database resets:**
1. Check if platform persists storage
2. Restore from backup
3. Switch to platform with persistent storage

**Prevention:**
- Use Railway (automatic persistence)
- Set up regular backups
- Don't use Heroku free tier (ephemeral filesystem)

---

## 💰 Cost Comparison

| Platform | Free Tier | Always-On | DB Persistence | Auto-Deploy |
|----------|-----------|-----------|----------------|-------------|
| Railway | 500 hrs/mo | ✅ Yes | ✅ Yes | ✅ Yes |
| Render | Unlimited | ⚠️ Sleeps | ✅ Yes | ✅ Yes |
| Fly.io | 3 VMs | ✅ Yes | ✅ Yes | ⚠️ Manual |
| Heroku | 550 hrs/mo | ⚠️ Sleeps | ❌ No | ✅ Yes |

**Recommendation:** Railway for simplest 24/7 operation with zero configuration.

---

## 📞 Support & Monitoring

### Admin Commands for Monitoring
```
/stats          - Bot statistics (users, transactions)
/allusers       - List all users
/likestatus     - Free Fire usage stats
```

### Log Monitoring
- Set up log aggregation (optional)
- Monitor for errors daily
- Check Free Fire API success rate

### Performance Metrics
- Response time: < 2 seconds
- Uptime target: 99.9% (8 hours downtime/year)
- Free Fire success rate: > 95%

---

## 🎉 Success Criteria for 24/7

Your bot is successfully running 24/7 when:

✅ Responds to `/start` within 2 seconds
✅ UptimeRobot shows 99%+ uptime
✅ Keep-Alive endpoint returns 200 OK
✅ Free Fire likes successfully sent
✅ No crashes in past 24 hours
✅ Database persists across restarts
✅ Admin commands working
✅ Users can transfer coins
✅ Payment approvals working

---

## 📅 Maintenance Schedule

**Daily:**
- Check UptimeRobot status
- Review error logs (if any)

**Weekly:**
- Check database size
- Review user growth
- Test Free Fire likes

**Monthly:**
- Backup database manually
- Update dependencies (if needed)
- Review Free Fire guest account pool

---

**Your bot is now ready for 24/7 operation!** 🚀

Deploy to Railway, set up UptimeRobot, and your RepotechBot will run continuously with all 161 Free Fire guest accounts ready to send likes to your users.
