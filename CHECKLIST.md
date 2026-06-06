# RepotechBot - Pre-Launch Checklist

Before running your bot, complete this checklist:

## 1. Environment Configuration

### Get Your Telegram User ID
- [ ] Open Telegram
- [ ] Search for [@userinfobot](https://t.me/userinfobot)
- [ ] Start the bot
- [ ] Copy your User ID number

### Update .env File
- [ ] Open `.env` file in a text editor
- [ ] Replace `ADMIN_ID=0` with `ADMIN_ID=your_user_id`
- [ ] Verify BOT_TOKEN is correct: `8963786165:AAGDcSbQxbv7sGUfrJK95TpeT-u7nJMO2ps`
- [ ] Verify UPI_ID is correct: `rsamofflceprv.ldt@fam`
- [ ] Save the file

Example `.env` file:
```env
BOT_TOKEN=8963786165:AAGDcSbQxbv7sGUfrJK95TpeT-u7nJMO2ps
ADMIN_ID=123456789  # Replace with your actual ID
UPI_ID=rsamofflceprv.ldt@fam
```

## 2. Python Setup

### Check Python Version
- [ ] Run `python3 --version`
- [ ] Ensure version is 3.9 or higher
- [ ] If not, install Python 3.9+

### Install Dependencies
Choose one method:

#### Method 1: Using run.sh (Recommended for Linux/Mac)
```bash
chmod +x run.sh
./run.sh
```

#### Method 2: Manual Installation
```bash
# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 3. Verify Installation

### Check Dependencies
- [ ] Run `pip list` and verify these packages are installed:
  - python-telegram-bot (20.8)
  - python-dotenv (1.0.0)
  - aiosqlite (0.19.0)
  - Flask (3.0.0)

### Test Import
- [ ] Run: `python -c "import telegram; print('OK')"`
- [ ] Should print "OK" without errors

## 4. Bot Configuration

### Verify Bot Token
- [ ] Open [@BotFather](https://t.me/BotFather) on Telegram
- [ ] Send `/mybots`
- [ ] Select your bot
- [ ] Click "API Token"
- [ ] Verify it matches the token in `.env`

### Test Bot Access
- [ ] Find your bot on Telegram
- [ ] Click "Start" (don't send commands yet)
- [ ] Bot should be accessible

## 5. File Permissions

### Linux/Mac Only
```bash
# Make sure all Python files are readable
chmod 644 *.py
chmod 644 handlers/*.py
chmod 644 utils/*.py
chmod 644 freefire/*.py

# Make run script executable
chmod +x run.sh
```

## 6. Pre-Launch Test

### Start the Bot
```bash
python bot.py
```

### Expected Output
You should see:
```
INFO - Starting RepotechBot...
INFO - Initializing database...
INFO - Database initialized successfully
INFO - Keep Alive server started
INFO - Starting Keep Alive server on port 8080
INFO - Bot started successfully! Press Ctrl+C to stop.
```

### If You See Errors

#### Error: "No module named 'telegram'"
**Solution**: Install dependencies with `pip install -r requirements.txt`

#### Error: "Invalid token"
**Solution**: Check BOT_TOKEN in `.env` file

#### Error: "Port 8080 already in use"
**Solution**: Edit `config.py` and change `KEEP_ALIVE_PORT = 8080` to another port

#### Error: "Permission denied"
**Solution**: Check file permissions or run with appropriate permissions

## 7. First Test

### Test Basic Commands
- [ ] Open your bot on Telegram
- [ ] Send `/start`
- [ ] Should receive welcome message
- [ ] Should show balance of 100 coins

### Test User Commands
- [ ] Send `/help` - Should show all commands
- [ ] Send `/balance` - Should show 100 coins
- [ ] Send `/daily` - Should give daily reward
- [ ] Send `/referral` - Should give referral link

### Test Admin Commands
Only if you're the admin (ADMIN_ID is set):
- [ ] Send `/admin` - Should show admin menu
- [ ] Send `/stats` - Should show bot statistics
- [ ] Send `/genkey 1 50` - Should generate a key
- [ ] Send `/redeem <key>` - Should redeem the key

## 8. Production Checklist

### Security
- [ ] Never share your `.env` file
- [ ] Never commit `.env` to git (already in .gitignore)
- [ ] Keep bot token secret
- [ ] Only share bot username, not token

### Backup
- [ ] Plan regular backups of `repotech_bot.db`
- [ ] Test restore procedure
- [ ] Store backups securely

### Monitoring
- [ ] Keep Alive server running on port 8080
- [ ] Monitor bot logs for errors
- [ ] Set up uptime monitoring (optional)

### Performance
- [ ] Test with multiple users
- [ ] Monitor database size
- [ ] Check response times

## 9. Optional Enhancements

### systemd Service (Linux)
- [ ] Create systemd service file
- [ ] Enable auto-start on boot
- [ ] Set up log rotation

### Cloud Deployment
- [ ] Choose platform (Heroku, Railway, Render, etc.)
- [ ] Configure environment variables
- [ ] Deploy and test
- [ ] Set up monitoring

### Domain & SSL (Optional)
- [ ] Get domain name
- [ ] Configure DNS
- [ ] Set up SSL certificate
- [ ] Point to Keep Alive server

## 10. Final Verification

### All Systems Check
- [ ] Bot responds to commands
- [ ] Database is working
- [ ] Transactions are saved
- [ ] Admin commands work
- [ ] Payment system works
- [ ] Referral system works
- [ ] Daily rewards work
- [ ] Transfer system works
- [ ] Keys redemption works
- [ ] Leaderboard works

### User Experience
- [ ] Commands are clear
- [ ] Error messages are helpful
- [ ] Success messages are informative
- [ ] Notifications work
- [ ] Inline buttons work (in /buy)

### Admin Experience
- [ ] Can manage users
- [ ] Can manage balances
- [ ] Can generate keys
- [ ] Can approve payments
- [ ] Can broadcast messages
- [ ] Can view statistics

## 11. Documentation Review

- [ ] Read README.md
- [ ] Read QUICKSTART.md
- [ ] Read PROJECT_SUMMARY.md
- [ ] Understand all features
- [ ] Know how to troubleshoot

## 12. Launch Preparation

### Announce to Users
- [ ] Prepare announcement message
- [ ] List all features
- [ ] Explain how to get started
- [ ] Share referral rewards info

### Support Plan
- [ ] Prepare FAQ
- [ ] Set up support channel
- [ ] Train support team (if any)
- [ ] Prepare common responses

### Marketing
- [ ] Share bot username
- [ ] Post on social media
- [ ] Join relevant groups
- [ ] Offer launch bonuses

## Completion

Once all items are checked:
- [ ] All checklist items completed
- [ ] Bot tested thoroughly
- [ ] Ready for launch
- [ ] Good to go!

---

## Need Help?

1. Check console logs for errors
2. Review README.md for troubleshooting
3. Test each feature individually
4. Contact developer if needed

## Quick Commands Reference

```bash
# Install dependencies
pip install -r requirements.txt

# Run bot
python bot.py

# Run with logging
python bot.py 2>&1 | tee bot.log

# Stop bot
Ctrl+C

# Check if bot is running
ps aux | grep bot.py
```

---

**Ready to launch?** 🚀

Start the bot with: `python bot.py` or `./run.sh`
