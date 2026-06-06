# RepotechBot - Telegram Coin Management Bot

A comprehensive Telegram bot for coin management, referral system, daily rewards, and Free Fire services.

## Features

### User Features
- **Coin Balance System**: Track and manage your coins
- **Referral System**: Earn 50 coins for each friend you refer
- **Daily Rewards**: Claim 10-50 coins every 24 hours
- **Transfer System**: Send coins to other users
- **Redeem Keys**: Use special keys to get coins (max 3 per day)
- **Buy Coins**: Purchase coin packages via UPI
- **Leaderboard**: See top 10 richest users
- **Transaction History**: View your last 5 transactions
- **Free Fire Likes**: Send likes to Free Fire UIDs (coming soon)

### Admin Features
- **User Management**: Ban/unban users, view user info
- **Balance Management**: Add/remove coins from any user
- **Key Generation**: Create redeem keys for users
- **Payment Approval**: Approve or reject coin purchases
- **Statistics**: View bot statistics
- **Broadcast**: Send messages to all users
- **User List**: See all users with balances

## Project Structure

```
repotech-telegram-bot/
├── bot.py                  # Main bot file
├── config.py              # Configuration and environment variables
├── database.py            # SQLite database handler
├── keep_alive.py          # Flask server for 24/7 uptime
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create from .env.example)
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore file
├── README.md             # This file
│
├── handlers/             # Command handlers
│   ├── __init__.py
│   ├── basic.py         # /start, /help
│   ├── balance.py       # /balance, /spend, /history
│   ├── admin.py         # All admin commands
│   ├── referral.py      # /referral, /referrals, /topref
│   ├── transfer.py      # /transfer
│   ├── redeem.py        # /redeem
│   ├── daily.py         # /daily
│   ├── leaderboard.py   # /leaderboard
│   ├── buy.py           # /buy, /paid
│   └── likes.py         # Free Fire likes (placeholder)
│
├── utils/               # Utility modules
│   ├── __init__.py
│   ├── decorators.py   # Admin check, banned check
│   └── helpers.py      # Helper functions
│
└── freefire/           # Free Fire integration
    ├── __init__.py
    └── likes_sender.py # Placeholder for Free Fire API
```

## Setup Instructions

### 1. Prerequisites
- Python 3.9 or higher
- A Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))
- Your Telegram User ID (get from [@userinfobot](https://t.me/userinfobot))

### 2. Installation

Clone the repository:
```bash
git clone <repository-url>
cd repotech-telegram-bot
```

Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file from the example:
```bash
cp .env.example .env
```

Edit `.env` and add your configuration:
```env
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_user_id
UPI_ID=your_upi_id_here
```

**Important**: Replace the placeholder values with your actual credentials.

### 4. Running the Bot

Start the bot:
```bash
python bot.py
```

The bot will:
1. Initialize the SQLite database
2. Start the Flask keep-alive server on port 8080
3. Begin polling for Telegram updates

### 5. Keep Bot Running 24/7

For production deployment, use a process manager like `systemd`, `supervisor`, or deploy to:
- Heroku
- Railway
- Render
- PythonAnywhere
- Replit

The Flask server (`keep_alive.py`) helps with uptime monitoring services.

## Commands Reference

### Basic Commands
| Command | Description |
|---------|-------------|
| `/start` | Start the bot and see welcome message |
| `/help` | Show all available commands |

### Balance Commands
| Command | Description |
|---------|-------------|
| `/balance` | Check your current coin balance |
| `/spend <amount>` | Deduct coins from your balance |
| `/history` | View your last 5 transactions |

### Referral Commands
| Command | Description |
|---------|-------------|
| `/referral` | Get your unique referral link |
| `/referrals` | See how many people you've referred |
| `/topref` | View top 10 referrers leaderboard |

### Reward Commands
| Command | Description |
|---------|-------------|
| `/daily` | Claim daily reward (10-50 coins, once per 24h) |
| `/redeem <key>` | Redeem a key for coins (max 3 per day) |

### Transfer & Buy Commands
| Command | Description |
|---------|-------------|
| `/transfer <user_id> <amount>` | Send coins to another user |
| `/buy` | View coin packages and purchase options |
| `/paid <package> <transaction_id>` | Submit payment proof |

### Statistics Commands
| Command | Description |
|---------|-------------|
| `/leaderboard` | See top 10 richest users |

### Free Fire Commands (Coming Soon)
| Command | Description |
|---------|-------------|
| `/likes <uid>` | Send Free Fire likes to a UID |
| `/likestatus` | Check your likes sending status |
| `/likehistory` | View your likes usage history |

### Admin Commands
| Command | Description |
|---------|-------------|
| `/admin` | Show admin commands menu |
| `/stats` | View bot statistics |
| `/allusers` | List all users with balances |
| `/userinfo <user_id>` | Get user information |
| `/ban <user_id>` | Ban a user |
| `/unban <user_id>` | Unban a user |
| `/resetuser <user_id>` | Reset user balance to 0 |
| `/addbalance <user_id> <amount>` | Add coins to user |
| `/removebalance <user_id> <amount>` | Remove coins from user |
| `/genkey <count> <coins>` | Generate redeem keys |
| `/listkeys` | List all unused keys |
| `/deletekey <key>` | Delete a specific key |
| `/approve <user_id> <coins>` | Approve coin purchase |
| `/reject <user_id> <reason>` | Reject coin purchase |
| `/broadcast <message>` | Send message to all users |

## Coin Packages

| Package | Coins | Price |
|---------|-------|-------|
| Package 1 | 50 | Rs.30 |
| Package 2 | 100 | Rs.50 |
| Package 3 | 200 | Rs.90 |

## Database Schema

The bot uses SQLite with the following tables:

- **users**: User information, balance, ban status
- **transactions**: Transaction history
- **referrals**: Referral tracking
- **keys**: Redeem keys
- **likes_usage**: Free Fire likes usage (placeholder)
- **payments**: Payment submissions

## Bot Configuration

Edit `config.py` to customize:
- Initial balance for new users (default: 100 coins)
- Referral rewards (default: 50 coins)
- Daily reward range (default: 10-50 coins)
- Maximum redeems per day (default: 3)
- Buy packages and prices
- Broadcast delay for rate limiting

## Safety Features

- **Ban Protection**: Admins cannot be banned
- **Rate Limiting**: Broadcast respects Telegram rate limits
- **Transaction Safety**: Coins never deducted on failed operations
- **Banned User Block**: Banned users cannot use any commands
- **Validation**: All inputs validated before processing

## Development

### Adding New Commands

1. Create handler in `handlers/` directory
2. Import in `bot.py`
3. Register with `application.add_handler()`
4. Add decorators for permission checks

### Using Decorators

```python
from utils.decorators import check_banned, user_exists, admin_only

@check_banned  # Prevent banned users
@user_exists   # Ensure user exists in DB
async def my_command(update, context):
    # Your code here
    pass

@admin_only    # Restrict to admin only
async def admin_command(update, context):
    # Your code here
    pass
```

## Free Fire Integration

The Free Fire likes system is currently a placeholder. Integration files are available at:
```
/workspace/claude-workspace/samdavistwo_gmail.com/uploads/freefire-like-and-guest-api-main/
```

To integrate:
1. Review the API files
2. Implement in `freefire/likes_sender.py`
3. Update handlers in `handlers/likes.py`
4. Configure pricing and limits

## Troubleshooting

### Bot not responding
- Check if bot token is correct
- Ensure bot is running (`python bot.py`)
- Check logs for errors

### Database errors
- Delete `repotech_bot.db` and restart bot
- Check file permissions

### Commands not working
- Ensure you've started the bot with `/start`
- Check if you're banned (contact admin)
- Verify command syntax

### Payment issues
- Ensure transaction ID is correct
- Wait for admin approval
- Contact admin if delayed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is private and proprietary.

## Support

For support, contact the bot administrator.

## Credits

Developed by RepotechBot Team

---

**Note**: This bot is for educational and private use. Ensure compliance with Telegram's Terms of Service and Bot API guidelines.
