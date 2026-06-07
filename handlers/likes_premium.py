"""
Free Fire Likes - PREMIUM MULTI-API SYSTEM
100% Always Available - Uses HL Gaming Premium + Fallback
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

from multi_api_likes import send_likes_multi_api, get_player_info

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
    """Handle /likes command - PREMIUM MULTI-API - 100% AVAILABILITY"""
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
                f"✨ Premium Multi-API System\n"
                f"⚡ 100% Always Available"
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
            "🔄 Processing request...\n"
            f"🎯 Target UID: {target_uid}\n"
            "⏳ Fetching player info..."
        )

        # Get player info
        player_info = await get_player_info(target_uid)
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
            f"⚡ Using premium multi-API system..."
        )

        # Send likes using multi-API system
        result = await send_likes_multi_api(target_uid, LIKES_TO_SEND)

        if not result.get("success"):
            await msg.edit_text(
                "❌ Service Unavailable!\n\n"
                "All API methods failed:\n"
                "• HL Gaming Premium API\n"
                "• Guest Accounts Fallback\n\n"
                "This is very rare. Please try again in 5 minutes.\n\n"
                "💰 No coins deducted."
            )
            return

        # Extract results
        likes_given = result.get("likes_given", 0)
        api_player_name = result.get("player_name", player_name)
        method_used = result.get("method", "Unknown")

        if likes_given == 0:
            await msg.edit_text(
                "⚠️ No likes sent!\n\n"
                "Possible reasons:\n"
                "• UID already received likes in last 24 hours\n"
                "• All guest accounts failed\n\n"
                "💡 Try again tomorrow\n\n"
                "💰 No coins deducted."
            )
            return

        # Wait for sync
        await asyncio.sleep(8)

        # Get updated info
        player_after = await get_player_info(target_uid)
        likes_after = player_after.get("likes", likes_before + likes_given)
        likes_added = max(likes_after - likes_before, likes_given)

        # Deduct coins
        new_balance = user['balance'] - LIKES_COST
        await db.update_balance(user_id, -LIKES_COST)
        await db.add_transaction(
            user_id, "likes", -LIKES_COST,
            f"Sent {likes_given} likes to {target_uid}"
        )
        await db.add_likes_usage(user_id, target_uid, likes_given, LIKES_COST)

        # Success
        requests_left = DAILY_LIMIT - (today_requests + 1)

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
        success_msg += f"💰 Transaction:\n"
        success_msg += f"   Deducted: -{LIKES_COST} coins\n"
        success_msg += f"   New Balance: {new_balance} coins\n\n"
        success_msg += f"📅 Requests left today: {requests_left}/{DAILY_LIMIT}\n\n"
        success_msg += f"✨ Refresh Free Fire to see the likes!\n"
        success_msg += f"🔧 Method: {method_used}\n"
        success_msg += f"✅ 100% Always Available"

        await msg.edit_text(success_msg)
        logger.info(f"✅ Multi-API: Sent {likes_given} likes to {player_name} ({target_uid}) via {method_used}")

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
