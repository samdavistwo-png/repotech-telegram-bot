"""
Configuration module for RepotechBot
Loads environment variables and stores bot configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required. Please set it in .env file")

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))  # Must be set in .env
if ADMIN_ID == 0:
    raise ValueError("ADMIN_ID environment variable is required. Please set it in .env file")

UPI_ID = os.getenv("UPI_ID", "rsamofflceprv.ldt@fam")

# Database Configuration
DATABASE_PATH = "repotech_bot.db"

# Bot Settings
INITIAL_BALANCE = 100  # Coins given to new users
REFERRAL_REWARD = 50  # Coins for both referrer and referee
DAILY_REWARD_MIN = 10  # Minimum daily reward
DAILY_REWARD_MAX = 50  # Maximum daily reward
MAX_REDEEMS_PER_DAY = 3  # Maximum key redemptions per user per day

# Buy Packages (amount in Rs, coins given)
BUY_PACKAGES = {
    "50_coins": {"coins": 50, "price": 30},
    "100_coins": {"coins": 100, "price": 50},
    "200_coins": {"coins": 200, "price": 90},
}

# Broadcast Settings
BROADCAST_DELAY = 0.05  # Delay between messages in seconds (50ms)

# Keep Alive Server
KEEP_ALIVE_PORT = 8080
