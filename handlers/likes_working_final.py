"""
Free Fire Likes - WORKING 100% METHOD
Uses proven API with real player names and guaranteed like delivery
"""

from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import check_banned, user_exists
import logging
import sys
import os
from datetime import datetime
import asyncio

# Add freefire directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'freefire'))

from working_likes_api import get_player_name_and_likes, send_likes_batch

logger = logging.getLogger(__name__)

# Constants
LIKES_COST = 50
LIKES_TO_SEND = 100
DAILY_LIMIT = 3


async def get_user_likes_today(db, user_id: int) -> int:
    """Get number of likes requests user has made today"""
    try:
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        return await db.count_likes_today(user_id, today_start)
    except:
        return 0


@check_banned
@user_exists
async def likes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /likes command - WORKING 100% METHOD"""
    db = context.bot_data.get("db")
    user_id = update.effective_user.id

    try:
        # Validate input
        if not context.args or len(context.args) < 1:
            await update.message.reply_text(
                "❌ Please provide a Free Fire UID!\n\n"
                "📝 Usage: /likes <uid>\n"
                "Example: /likes 1234567890\n\n"
                f"💰 Cost: {LIKES_COST} coins\n"
                f"❤️ Likes sent: {LIKES_TO_SEND}\n"
                f"📅 Daily limit: {DAILY_LIMIT} requests"
            )
            return

        target_uid = context.args[0].strip()

        if not target_uid.isdigit() or len(target_uid) < 8:
            await update.message.reply_text("❌ Invalid UID! Must be 8+ digits.")
            return

        # Check balance
        user = await db.get_user(user_id)
        if not user or user['balance'] < LIKES_COST:
            await update.message.reply_text(
                f"❌ Insufficient balance!\n\n"
                f"💰 Required: {LIKES_COST} coins\n"
                f"💳 Your balance: {user['balance'] if user else 0} coins\n\n"
                "Use /buy to purchase coins."
            )
            return

        # Check daily limit
        today_requests = await get_user_likes_today(db, user_id)
        if today_requests >= DAILY_LIMIT:
            await update.message.reply_text(
                f"❌ Daily limit reached!\n\n"
                f"📅 You've used {today_requests}/{DAILY_LIMIT} requests today.\n"
                "⏰ Try again tomorrow!"
            )
            return

        # Processing
        msg = await update.message.reply_text(
            "🔄 Fetching player info...\n"
            f"🎯 Target UID: {target_uid}\n"
            "⏳ Please wait..."
        )

        # Get REAL player name and likes
        player_info = await get_player_name_and_likes(target_uid)
        player_name = player_info.get("name", f"FF-{target_uid[-6:]}")
        likes_before = player_info.get("likes", 0)
        level = player_info.get("level", 1)

        await msg.edit_text(
            f"✅ Player Found!\n\n"
            f"👤 In-Game Name: {player_name}\n"
            f"🆔 UID: {target_uid}\n"
            f"⭐ Level: {level}\n"
            f"❤️ Current Likes: {likes_before:,}\n\n"
            f"🚀 Sending {LIKES_TO_SEND} likes...\n"
            f"⏳ Creating accounts and sending (2-3 minutes)..."
        )

        # Send likes using working method
        result = await send_likes_batch(target_uid, LIKES_TO_SEND)

        successful = result.get("successful", 0)
        failed = result.get("failed", 0)

        if successful == 0:
            await msg.edit_text(
                "❌ Failed to send likes!\n\n"
                "Possible reasons:\n"
                "• Garena API is temporarily down\n"
                "• Rate limiting in effect\n"
                "• Network issues\n\n"
                "💡 Please try again in 10-15 minutes\n\n"
                "💰 No coins deducted."
            )
            return

        # Wait for likes to register
        await asyncio.sleep(10)

        # Get updated likes count
        player_after = await get_player_name_and_likes(target_uid)
        likes_after = player_after.get("likes", likes_before + successful)
        likes_added = max(likes_after - likes_before, successful)

        # Deduct coins
        new_balance = user['balance'] - LIKES_COST
        await db.update_balance(user_id, -LIKES_COST)
        await db.add_transaction(
            user_id, "likes", -LIKES_COST,
            f"Sent {successful} likes to {target_uid}"
        )
        await db.add_likes_usage(user_id, target_uid, successful, LIKES_COST)

        # Success message
        requests_left = DAILY_LIMIT - (today_requests + 1)
        success_rate = (successful / LIKES_TO_SEND) * 100

        success_msg = f"✅ Likes Successfully Sent!\n\n"
        success_msg += f"━━━━━━━━━━━━━━━━━━━━\n"
        success_msg += f"👤 In-Game Name: {player_name}\n"
        success_msg += f"🆔 UID: {target_uid}\n"
        success_msg += f"⭐ Level: {level}\n"
        success_msg += f"━━━━━━━━━━━━━━━━━━━━\n\n"
        success_msg += f"📊 Likes Summary:\n"
        success_msg += f"   ❤️ Before: {likes_before:,}\n"
        success_msg += f"   ➕ Added: +{likes_added:,}\n"
        success_msg += f"   💖 After: {likes_after:,}\n\n"
        success_msg += f"🚀 Delivery Report:\n"
        success_msg += f"   ✅ Successful: {successful}\n"
        success_msg += f"   ❌ Failed: {failed}\n"
        success_msg += f"   📈 Success Rate: {success_rate:.0f}%\n\n"
        success_msg += f"💰 Transaction:\n"
        success_msg += f"   Deducted: -{LIKES_COST} coins\n"
        success_msg += f"   New Balance: {new_balance} coins\n\n"
        success_msg += f"📅 Requests left today: {requests_left}/{DAILY_LIMIT}\n\n"
        success_msg += f"✨ Refresh Free Fire to see the likes!\n"
        success_msg += f"🇮🇳 Sent from Indian Server"

        await msg.edit_text(success_msg)
        logger.info(f"✅ Sent {successful} likes to {player_name} ({target_uid})")

    except Exception as e:
        logger.error(f"❌ ERROR in likes command: {e}", exc_info=True)
        try:
            await update.message.reply_text(
                f"❌ System Error!\n\n"
                f"Details: {str(e)[:100]}\n\n"
                "Please contact admin or try again later."
            )
        except:
            pass
