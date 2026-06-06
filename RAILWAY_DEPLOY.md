# Deploy to Railway - Quick Guide

## Your Bot Configuration (Pre-configured)

✅ **Bot Token:** 8963786165:AAGDcSbQxbv7sGUfrJK95TpeT-u7nJMO2ps
✅ **Admin ID:** 6550771842
✅ **UPI ID:** rsamofflceprv.ldt@fam

All environment variables are already set in the `.env` file!

---

## Deploy to Railway (5 Minutes)

### Step 1: Sign Up/Login (1 minute)
1. Go to: https://railway.app
2. Click **"Login"**
3. Choose **"Login with GitHub"**
4. Authorize Railway to access your GitHub

### Step 2: Create New Project (1 minute)
1. Click **"New Project"** button
2. Select **"Deploy from GitHub repo"**
3. Find and click: **`repotech-telegram-bot`**
4. Railway will automatically start deploying

### Step 3: Environment Variables (2 minutes)
Even though `.env` exists, Railway needs these set in their dashboard:

1. In Railway dashboard, find your project
2. Click **"Variables"** tab on the left
3. Click **"+ New Variable"** and add these **ONE BY ONE**:

```
BOT_TOKEN
8963786165:AAGDcSbQxbv7sGUfrJK95TpeT-u7nJMO2ps

ADMIN_ID
6550771842

UPI_ID
rsamofflceprv.ldt@fam
```

**Important:** Type each variable name in the "Key" field and its value in the "Value" field.

### Step 4: Watch Deployment (1 minute)
1. Click **"Deployments"** tab
2. Watch the logs - you'll see:
   ```
   Installing dependencies...
   Starting bot...
   INFO - Bot started successfully!
   ```

### Step 5: Test Your Bot (30 seconds)
1. Open Telegram
2. Search for your bot username
3. Send `/start`
4. **Bot should respond immediately!**

---

## Verify Everything Works

Send these commands to your bot:

```
/start          → Welcome message + 100 coins
/help           → Command list
/balance        → Shows 100 coins
/admin          → Admin panel (you're the admin!)
/stats          → Bot statistics
```

---

## Test Free Fire Likes

1. Get a Free Fire UID (any valid UID from IND server)
2. Send: `/likes 123456789` (replace with real UID)
3. Bot will send 100 likes using the 161 guest accounts!

---

## Your Bot is Now Running 24/7!

✅ No need for UptimeRobot (Railway doesn't sleep)
✅ All 161 Free Fire guest accounts ready
✅ Admin commands available to you only
✅ Database persists automatically
✅ Free tier: 500 hours/month (20+ days continuous)

---

## Troubleshooting

**Bot not responding?**
1. Check Railway logs for errors
2. Verify environment variables are set correctly
3. Make sure BOT_TOKEN is correct

**Need to update environment variables?**
1. Go to Railway dashboard
2. Click "Variables" tab
3. Edit the value
4. Railway will automatically restart the bot

---

## Alternative: One-Click Deploy Button

Click this button to deploy instantly:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/samdavistwo-png/repotech-telegram-bot)

Then just set the environment variables in Railway dashboard!

---

**Your bot is ready to deploy right now!** 🚀
