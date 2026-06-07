"""
RepotechBot - Main Bot File
A comprehensive Telegram bot for coin management, referrals, and Free Fire services
"""

import logging
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

# Import configuration
from config import BOT_TOKEN

# Import database
from database import Database

# Import handlers
from handlers.basic import start_command, help_command
from handlers.balance import balance_command, spend_command, history_command
from handlers.admin import (
    admin_command,
    stats_command,
    broadcast_command,
    ban_command,
    unban_command,
    addbalance_command,
    removebalance_command,
    allusers_command,
    resetuser_command,
    genkey_command,
    listkeys_command,
    deletekey_command,
    approve_command,
    reject_command,
    userinfo_command,
    sysinfo_command,
)
from handlers.referral import (
    referral_command,
    referrals_command,
    topref_command,
)
from handlers.transfer import transfer_command
from handlers.redeem import redeem_command
from handlers.daily import daily_command
from handlers.leaderboard import leaderboard_command
from handlers.buy import buy_command, buy_callback, paid_command
# Use simple direct API method instead of auth server
from handlers.likes_simple import likes_command
from handlers.likes import (
    likestatus_command,
    likehistory_command,
)
from handlers.apihealth import apihealth_command

# Import keep alive
from keep_alive import keep_alive

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def post_init(application: Application):
    """Initialize database and bot data after application start"""
    logger.info("Initializing database...")
    db = Database()
    await db.init_db()
    application.bot_data["db"] = db
    logger.info("Database initialized successfully")


async def error_handler(update, context):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")


def main():
    """Main function to run the bot"""
    logger.info("Starting RepotechBot...")

    # Create application
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Basic commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))

    # Balance commands
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("spend", spend_command))
    application.add_handler(CommandHandler("history", history_command))

    # Admin commands
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("ban", ban_command))
    application.add_handler(CommandHandler("unban", unban_command))
    application.add_handler(CommandHandler("addbalance", addbalance_command))
    application.add_handler(CommandHandler("removebalance", removebalance_command))
    application.add_handler(CommandHandler("allusers", allusers_command))
    application.add_handler(CommandHandler("resetuser", resetuser_command))
    application.add_handler(CommandHandler("genkey", genkey_command))
    application.add_handler(CommandHandler("listkeys", listkeys_command))
    application.add_handler(CommandHandler("deletekey", deletekey_command))
    application.add_handler(CommandHandler("approve", approve_command))
    application.add_handler(CommandHandler("reject", reject_command))
    application.add_handler(CommandHandler("userinfo", userinfo_command))
    application.add_handler(CommandHandler("sysinfo", sysinfo_command))

    # Referral commands
    application.add_handler(CommandHandler("referral", referral_command))
    application.add_handler(CommandHandler("referrals", referrals_command))
    application.add_handler(CommandHandler("topref", topref_command))

    # Transfer command
    application.add_handler(CommandHandler("transfer", transfer_command))

    # Redeem command
    application.add_handler(CommandHandler("redeem", redeem_command))

    # Daily reward command
    application.add_handler(CommandHandler("daily", daily_command))

    # Leaderboard command
    application.add_handler(CommandHandler("leaderboard", leaderboard_command))

    # Buy commands
    application.add_handler(CommandHandler("buy", buy_command))
    application.add_handler(CommandHandler("paid", paid_command))
    application.add_handler(CallbackQueryHandler(buy_callback, pattern="^buy_"))

    # Free Fire likes commands
    application.add_handler(CommandHandler("likes", likes_command))
    application.add_handler(CommandHandler("likestatus", likestatus_command))
    application.add_handler(CommandHandler("likehistory", likehistory_command))

    # API Health Check command (admin only)
    application.add_handler(CommandHandler("apihealth", apihealth_command))

    # Error handler
    application.add_error_handler(error_handler)

    # Start keep alive server
    keep_alive()

    # Start bot
    logger.info("Bot started successfully! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
