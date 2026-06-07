"""
Free Fire Likes - INSTANT DELIVERY
Uses HL Gaming Official API - Production-ready service
Super fast like /transfer command
"""

from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import check_banned, user_exists
import logging
import sys
import os
from datetime import datetime

# Add freefire directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'freefire'))

from hlgaming_api import send_likes_hlgaming, get_player_info_hlgaming

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
    """Handle /likes command - INSTANT DELIVERY like /transfer"""
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
                f"❤️ Likes sent: Up to 100\n"
                f"📅 Daily limit: {DAILY_LIMIT} requests\n"
                f"⚡ Instant delivery!"
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

        # Processing - INSTANT
        msg = await update.message.reply_text(
            "⚡ Sending likes instantly...\n"
            f"🎯 Target UID: {target_uid}\n"
            "⏳ Please wait..."
        )

        # Send likes using HL Gaming API - INSTANT
        result = await send_likes_hlgaming(target_uid, region="IND")

        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            await msg.edit_text(
                f"❌ Service Error!\n\n"
                f"Details: {error_msg}\n\n"
                f"The HL Gaming API may be:\n"
                f"• Temporarily down\n"
                f"• Rate limiting\n"
                f"• Requires API key update\n\n"
                f"💡 Try again in a few minutes\n\n"
                f"💰 No coins deducted."
            )
            return

        # Extract results
        player_name = result.get("player_name", f"FF-{target_uid[-6:]}")
        likes_before = result.get("likes_before", 0)
        likes_after = result.get("likes_after", 0)
        likes_given = result.get("likes_given", 0)

        if likes_given == 0:
            await msg.edit_text(
                "⚠️ No likes sent!\n\n"
                "Possible reasons:\n"
                "• This UID already received likes in last 24 hours\n"
                "• UID may be invalid\n"
                "• Service daily limit reached\n\n"
                "💡 Try again tomorrow\n\n"
                "💰 No coins deducted."
            )
            return

        # Deduct coins
        new_balance = user['balance'] - LIKES_COST
        await db.update_balance(user_id, -LIKES_COST)
        await db.add_transaction(
            user_id, "likes", -LIKES_COST,
            f"Sent {likes_given} likes to {target_uid}"
        )
        await db.add_likes_usage(user_id, target_uid, likes_given, LIKES_COST)

        # Success - INSTANT
        requests_left = DAILY_LIMIT - (today_requests + 1)

        success_msg = f"✅ Likes Delivered Instantly!\n\n"
        success_msg += f"━━━━━━━━━━━━━━━━━━━━\n"
        success_msg += f"👤 In-Game Name: {player_name}\n"
        success_msg += f"🆔 UID: {target_uid}\n"
        success_msg += f"━━━━━━━━━━━━━━━━━━━━\n\n"
        success_msg += f"📊 Likes Summary:\n"
        success_msg += f"   ❤️ Before: {likes_before:,}\n"
        success_msg += f"   ➕ Added: +{likes_given:,}\n"
        success_msg += f"   💖 After: {likes_after:,}\n\n"
        success_msg += f"💰 Transaction:\n"
        success_msg += f"   Deducted: -{LIKES_COST} coins\n"
        success_msg += f"   New Balance: {new_balance} coins\n\n"
        success_msg += f"📅 Requests left today: {requests_left}/{DAILY_LIMIT}\n\n"
        success_msg += f"✨ Refresh Free Fire to see the likes!\n"
        success_msg += f"⚡ Powered by HL Gaming API"

        await msg.edit_text(success_msg)
        logger.info(f"✅ INSTANT: Sent {likes_given} likes to {player_name} ({target_uid})")

    except Exception as e:
        logger.error(f"❌ ERROR in likes command: {e}", exc_info=True)
        try:
            await update.message.reply_text(
                f"❌ System Error!\n\n"
                f"Details: {str(e)[:100]}\n\n"
                "Please contact admin."
            )
        except:
            pass
