"""
Leaderboard command handler for RepotechBot
Handles /leaderboard command
"""

from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import check_banned, user_exists
import logging

logger = logging.getLogger(__name__)


@check_banned
@user_exists
async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /leaderboard command"""
    db = context.bot_data.get("db")
    user_id = update.effective_user.id

    # Get top 10 users
    top_users = await db.get_leaderboard(limit=10)

    if not top_users:
        await update.message.reply_text(
            "🏆 Leaderboard\n\n"
            "No users found yet. Be the first!"
        )
        return

    leaderboard_text = "🏆 Top 10 Richest Users\n\n"

    medals = {1: "🥇", 2: "🥈", 3: "🥉"}

    user_rank = None

    for idx, user in enumerate(top_users, 1):
        medal = medals.get(idx, f"{idx}.")
        username = user['username'] or f"User {user['user_id']}"
        balance = user['balance']

        # Check if current user is in top 10
        if user['user_id'] == user_id:
            user_rank = idx
            leaderboard_text += f"{medal} @{username} (You)\n   💰 {balance:,} coins\n\n"
        else:
            leaderboard_text += f"{medal} @{username}\n   💰 {balance:,} coins\n\n"

    # If user is not in top 10, show their rank
    if not user_rank:
        current_user = await db.get_user(user_id)
        leaderboard_text += f"━━━━━━━━━━━━━━━━━\n"
        leaderboard_text += f"👤 Your Balance: {current_user['balance']:,} coins\n"
        leaderboard_text += f"💡 Keep earning to reach the top 10!"

    await update.message.reply_text(leaderboard_text)
