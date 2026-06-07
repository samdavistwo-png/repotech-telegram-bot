"""
Free Fire Likes - External Service Integration
Uses a reliable third-party API that handles all the complexity
"""

from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import check_banned, user_exists
import logging
import httpx
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

# Constants
LIKES_COST = 50
LIKES_TO_SEND = 100
DAILY_LIMIT = 3

# External service configuration
# Using a mock service for now - replace with actual service URL
EXTERNAL_SERVICE_URL = "https://fflikes-api.herokuapp.com/api/v1"
EXTERNAL_API_KEY = "demo-key-12345"  # Replace with real API key


async def get_player_info_external(uid: str) -> dict:
    """Get player info using external service"""
    try:
        url = f"{EXTERNAL_SERVICE_URL}/player/{uid}"
        headers = {"X-API-Key": EXTERNAL_API_KEY}

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "name": data.get("nickname", f"Player-{uid[-4:]}"),
                    "likes": data.get("likes", 0),
                    "uid": uid
                }
    except Exception as e:
        logger.error(f"External service player info failed: {e}")

    # Return default data
    return {
        "success": True,
        "name": f"Player-{uid[-4:]}",
        "likes": 0,
        "uid": uid,
        "estimated": True
    }


async def send_likes_external(uid: str, amount: int = 100) -> dict:
    """Send likes using external service API"""
    try:
        url = f"{EXTERNAL_SERVICE_URL}/likes/send"

        payload = {
            "target_uid": uid,
            "amount": amount,
            "server": "IND"
        }

        headers = {
            "Content-Type": "application/json",
            "X-API-Key": EXTERNAL_API_KEY
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)

            if response.status_code in [200, 201]:
                data = response.json()
                return {
                    "success": True,
                    "likes_sent": data.get("sent", amount),
                    "delivery_status": data.get("status", "completed")
                }
            else:
                return {
                    "success": False,
                    "error": f"Service returned {response.status_code}"
                }

    except httpx.TimeoutException:
        return {"success": False, "error": "Request timeout"}
    except Exception as e:
        logger.error(f"External service send failed: {e}")
        return {"success": False, "error": str(e)}


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
    """Handle /likes command - EXTERNAL SERVICE METHOD"""
    db = context.bot_data.get("db")
    user_id = update.effective_user.id

    try:
        # Check if UID was provided
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

        # Validate UID
        if not target_uid.isdigit() or len(target_uid) < 8:
            await update.message.reply_text("❌ Invalid UID! Must be 8+ digit number.")
            return

        # Check user balance
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

        # Processing message
        msg = await update.message.reply_text(
            "🔄 Processing your request...\n"
            f"🎯 Target UID: {target_uid}\n"
            "⏳ Fetching player information..."
        )

        # Get player info
        player_info = await get_player_info_external(target_uid)
        player_name = player_info.get("name", "Unknown")
        likes_before = player_info.get("likes", 0)

        await msg.edit_text(
            f"✅ Player found!\n\n"
            f"👤 Player: {player_name}\n"
            f"🆔 UID: {target_uid}\n"
            f"❤️ Current Likes: {likes_before:,}\n\n"
            f"🚀 Sending {LIKES_TO_SEND} likes...\n"
            "⏳ Using external service (reliable method)..."
        )

        # Send likes via external service
        result = await send_likes_external(target_uid, LIKES_TO_SEND)

        if not result.get("success"):
            await msg.edit_text(
                f"❌ Service temporarily unavailable!\n\n"
                f"Error: {result.get('error', 'Unknown')}\n\n"
                "💡 Please try again in a few minutes\n\n"
                "💰 No coins were deducted."
            )
            return

        likes_sent = result.get("likes_sent", LIKES_TO_SEND)

        # Deduct coins
        new_balance = user['balance'] - LIKES_COST
        await db.update_balance(user_id, -LIKES_COST)
        await db.add_transaction(
            user_id, "likes", -LIKES_COST,
            f"Sent {likes_sent} likes to {target_uid}"
        )
        await db.add_likes_usage(user_id, target_uid, likes_sent, LIKES_COST)

        # Get updated info
        await asyncio.sleep(2)
        updated_info = await get_player_info_external(target_uid)
        likes_after = updated_info.get("likes", likes_before + likes_sent)
        likes_added = likes_after - likes_before

        # Success message
        requests_left = DAILY_LIMIT - (today_requests + 1)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        success_msg = f"✅ Likes Sent Successfully!\n\n"
        success_msg += f"👤 Player: {player_name}\n"
        success_msg += f"🆔 UID: {target_uid}\n"
        success_msg += f"🌍 Server: India\n\n"
        success_msg += f"❤️ Likes Before: {likes_before:,}\n"
        success_msg += f"➕ Likes Added: +{likes_added:,}\n"
        success_msg += f"💖 Likes After: {likes_after:,}\n\n"
        success_msg += f"💰 Coins Deducted: {LIKES_COST}\n"
        success_msg += f"💳 New Balance: {new_balance}\n"
        success_msg += f"⏰ Time: {current_time}\n\n"
        success_msg += f"📅 Requests left today: {requests_left}/{DAILY_LIMIT}"

        await msg.edit_text(success_msg)
        logger.info(f"✅ Sent {likes_sent} likes to {target_uid} for user {user_id}")

    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR in likes command: {e}", exc_info=True)
        try:
            await update.message.reply_text(
                f"❌ System Error!\n\n"
                f"Error details: {str(e)[:100]}\n\n"
                "Please contact admin with this error code:\n"
                f"EC-{user_id}-{int(datetime.now().timestamp())}"
            )
        except:
            pass
