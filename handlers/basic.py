"""
Basic command handlers for RepotechBot
Handles /start and /help commands
"""

from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import check_banned
from config import REFERRAL_REWARD
import logging

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    db = context.bot_data.get("db")
    user_id = update.effective_user.id
    username = update.effective_user.username

    # Check if user exists
    user = await db.get_user(user_id)

    if not user:
        # Check for referral code
        referred_by = None
        if context.args:
            try:
                referrer_id = int(context.args[0])
                referrer = await db.get_user(referrer_id)

                # Validate referrer exists and is not the same user
                if referrer and referrer_id != user_id:
                    referred_by = referrer_id
            except (ValueError, IndexError):
                pass

        # Create new user
        await db.create_user(user_id, username, referred_by)
        logger.info(f"New user registered: {user_id} (referred by: {referred_by})")

        # Process referral reward
        if referred_by:
            # Add referral record
            await db.add_referral(referred_by, user_id)

            # Give rewards to both users
            await db.update_balance(referred_by, REFERRAL_REWARD)
            await db.add_transaction(
                referred_by, "referral", REFERRAL_REWARD, f"Referral reward for inviting user {user_id}"
            )

            await db.update_balance(user_id, REFERRAL_REWARD)
            await db.add_transaction(
                user_id, "referral", REFERRAL_REWARD, f"Referral bonus"
            )

            # Notify referrer
            try:
                referrer_user = await db.get_user(referred_by)
                await context.bot.send_message(
                    chat_id=referred_by,
                    text=f"🎉 Congratulations! User @{username or user_id} joined using your referral link!\n\n"
                    f"💰 You received {REFERRAL_REWARD} coins as a reward!\n"
                    f"💼 New balance: {referrer_user['balance'] + REFERRAL_REWARD} coins",
                )
            except Exception as e:
                logger.error(f"Failed to notify referrer {referred_by}: {e}")

    # Check if user is banned
    user = await db.get_user(user_id)
    if user["is_banned"]:
        await update.message.reply_text(
            "❌ You have been banned from using this bot.\n"
            "Contact the administrator if you believe this is a mistake."
        )
        return

    # Welcome message
    welcome_text = f"""
🤖 Welcome to RepotechBot!

👤 User: @{username or user_id}
💰 Balance: {user['balance']} coins

📋 Available Commands:

💵 Balance & Transactions:
/balance - Check your coin balance
/history - View transaction history
/spend <amount> - Spend coins

👥 Referral System:
/referral - Get your referral link
/referrals - View referral count
/topref - Top 10 referrers

🎁 Rewards:
/daily - Claim daily reward (24h)
/redeem <key> - Redeem a key

💸 Transfer & Buy:
/transfer <user_id> <amount> - Send coins
/buy - Purchase coin packages

📊 Statistics:
/leaderboard - Top 10 richest users

🎮 Free Fire Services:
/likes <uid> - Send Free Fire likes
/likestatus - Check likes status
/likehistory - View likes history

ℹ️ Help:
/help - Show all commands

💎 Start earning coins and enjoy our services!
"""
    await update.message.reply_text(welcome_text)


@check_banned
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
📚 RepotechBot Commands Help

💵 BALANCE & TRANSACTIONS:
/balance - Check your current coin balance
/history - View your last 5 transactions
/spend <amount> - Deduct coins from your balance

👥 REFERRAL SYSTEM:
/referral - Get your unique referral link
/referrals - See how many people you've referred
/topref - View top 10 referrers leaderboard

🎁 REWARDS:
/daily - Claim daily reward (10-50 coins, once per 24h)
/redeem <key> - Redeem a key for coins (max 3/day)

💸 TRANSFER & BUY:
/transfer <user_id> <amount> - Transfer coins to another user
/buy - View coin packages and purchase

📊 STATISTICS:
/leaderboard - See top 10 richest users

🎮 FREE FIRE SERVICES:
/likes <uid> - Send Free Fire likes to a UID
/likestatus - Check your likes sending status
/likehistory - View your likes usage history

ℹ️ SUPPORT:
/help - Show this help message
/start - Return to main menu

💡 Tips:
- Refer friends to earn 50 coins each!
- Claim daily rewards every 24 hours
- Check leaderboard to see top users
- Use /buy to purchase more coins

Need assistance? Contact our support team!
"""
    await update.message.reply_text(help_text)
