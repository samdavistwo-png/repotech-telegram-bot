"""
Daily reward command handler for RepotechBot
Handles /daily command
"""

from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import check_banned, user_exists
from utils.helpers import can_claim_daily, time_until_next_daily
from config import DAILY_REWARD_MIN, DAILY_REWARD_MAX
import random
import logging

logger = logging.getLogger(__name__)


@check_banned
@user_exists
async def daily_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /daily command"""
    db = context.bot_data.get("db")
    user_id = update.effective_user.id

    # Get user
    user = await db.get_user(user_id)

    # Check if user can claim daily
    if not can_claim_daily(user["last_daily"]):
        time_remaining = time_until_next_daily(user["last_daily"])
        await update.message.reply_text(
            f"⏰ Daily Reward Already Claimed!\n\n"
            f"You can claim your next daily reward in:\n"
            f"⏳ {time_remaining}\n\n"
            f"Come back later!"
        )
        return

    # Generate random reward
    reward = random.randint(DAILY_REWARD_MIN, DAILY_REWARD_MAX)

    # Add reward
    await db.update_balance(user_id, reward)
    await db.add_transaction(user_id, "daily", reward, "Daily reward")
    await db.update_last_daily(user_id)

    # Get updated balance
    updated_user = await db.get_user(user_id)

    await update.message.reply_text(
        f"🎁 Daily Reward Claimed!\n\n"
        f"💰 You received: {reward} coins\n"
        f"💵 New balance: {updated_user['balance']:,} coins\n\n"
        f"⏰ Come back in 24 hours for your next reward!"
    )

    logger.info(f"User {user_id} claimed daily reward of {reward} coins")
