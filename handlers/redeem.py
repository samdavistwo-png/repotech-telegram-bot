"""
Redeem command handler for RepotechBot
Handles /redeem command
"""

from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import check_banned, user_exists
from config import MAX_REDEEMS_PER_DAY
import logging

logger = logging.getLogger(__name__)


@check_banned
@user_exists
async def redeem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /redeem command"""
    db = context.bot_data.get("db")
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text(
            "❌ Usage: /redeem <key>\n\n"
            "Example: /redeem abc123def456\n\n"
            f"💡 You can redeem up to {MAX_REDEEMS_PER_DAY} keys per day"
        )
        return

    key = context.args[0]

    # Check daily redeem limit
    redeems_today = await db.count_redeems_today(user_id)
    if redeems_today >= MAX_REDEEMS_PER_DAY:
        await update.message.reply_text(
            f"❌ Daily Redeem Limit Reached!\n\n"
            f"You have already redeemed {MAX_REDEEMS_PER_DAY} keys today.\n"
            f"Please try again tomorrow."
        )
        return

    # Get key from database
    key_data = await db.get_key(key)

    if not key_data:
        await update.message.reply_text(
            "❌ Invalid key!\n\n"
            "This key does not exist. Please check the key and try again."
        )
        return

    # Check if key is already used
    if key_data["is_used"]:
        await update.message.reply_text(
            "❌ Key Already Used!\n\n"
            "This key has already been redeemed."
        )
        return

    # Redeem key
    coins = key_data["coins"]

    await db.update_balance(user_id, coins)
    await db.add_transaction(user_id, "redeem", coins, f"Redeemed key: {key}")
    await db.redeem_key(key, user_id)

    # Get updated balance
    user = await db.get_user(user_id)

    await update.message.reply_text(
        f"🎁 Key Redeemed Successfully!\n\n"
        f"💰 Coins received: {coins:,}\n"
        f"💵 New balance: {user['balance']:,} coins\n\n"
        f"📊 Redeems today: {redeems_today + 1}/{MAX_REDEEMS_PER_DAY}"
    )

    logger.info(f"User {user_id} redeemed key {key} for {coins} coins")
