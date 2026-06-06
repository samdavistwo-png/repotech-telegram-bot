# RepotechBot - Quick Start Guide

Get your bot up and running in 5 minutes!

## Step 1: Set Your Admin ID

Open `.env` file and replace `ADMIN_ID=0` with your Telegram User ID:

```env
ADMIN_ID=your_telegram_user_id_here
```

To get your Telegram User ID:
1. Open Telegram
2. Search for [@userinfobot](https://t.me/userinfobot)
3. Start the bot
4. Copy your user ID
5. Paste it in the `.env` file

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 3: Run the Bot

```bash
python bot.py
```

You should see:
```
INFO - Starting RepotechBot...
INFO - Initializing database...
INFO - Database initialized successfully
INFO - Keep Alive server started
INFO - Bot started successfully! Press Ctrl+C to stop.
```

## Step 4: Test the Bot

1. Open Telegram
2. Search for your bot
3. Send `/start` command
4. You should receive a welcome message with your balance of 100 coins

## Step 5: Test Admin Commands

Send `/admin` to see all admin commands.

## Common Issues

### Issue: "No module named 'telegram'"
**Solution**: Install dependencies with `pip install -r requirements.txt`

### Issue: Bot not responding
**Solution**:
- Check if BOT_TOKEN is correct in `.env`
- Ensure bot is running
- Check console for errors

### Issue: Admin commands don't work
**Solution**: Make sure ADMIN_ID in `.env` matches your Telegram User ID

### Issue: Port 8080 already in use
**Solution**: Edit `config.py` and change `KEEP_ALIVE_PORT` to another port

## Next Steps

1. **Test User Features**:
   - `/balance` - Check balance
   - `/daily` - Claim daily reward
   - `/referral` - Get referral link
   - `/leaderboard` - See top users

2. **Test Admin Features**:
   - `/stats` - View statistics
   - `/genkey 5 100` - Generate 5 keys worth 100 coins each
   - `/addbalance <user_id> 50` - Add coins to a user

3. **Test Payment System**:
   - Send `/buy` to see packages
   - Click a package to see payment details
   - Submit with `/paid 50_coins TEST123`
   - Approve with `/approve <user_id> 50`

4. **Test Referral System**:
   - Get referral link with `/referral`
   - Share with another account
   - Have them click and start bot
   - Both accounts get 50 coins

## Production Deployment

### Option 1: VPS/Server
```bash
# Install screen or tmux
sudo apt install screen

# Start in detached session
screen -dmS repobot python bot.py

# To view logs
screen -r repobot
```

### Option 2: systemd Service
Create `/etc/systemd/system/repobot.service`:
```ini
[Unit]
Description=RepotechBot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/repotech-telegram-bot
ExecStart=/usr/bin/python3 /path/to/repotech-telegram-bot/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable repobot
sudo systemctl start repobot
sudo systemctl status repobot
```

### Option 3: Cloud Platforms
- **Heroku**: Add `Procfile` with `worker: python bot.py`
- **Railway**: Auto-detects Python and runs `bot.py`
- **Render**: Set start command to `python bot.py`

## File Structure Overview

```
repotech-telegram-bot/
├── bot.py              # Main bot - START HERE
├── config.py           # Configuration settings
├── database.py         # Database operations
├── keep_alive.py       # Web server for uptime
├── handlers/           # Command handlers
├── utils/              # Helper functions
└── freefire/           # Free Fire integration (placeholder)
```

## Support

Need help? Check:
1. README.md for detailed documentation
2. Console logs for errors
3. Contact admin if needed

## Security Notes

- Never share your `.env` file
- Never commit `.env` to git (already in .gitignore)
- Keep your bot token secret
- Regularly backup your database (`repotech_bot.db`)

---

Happy botting! 🤖
