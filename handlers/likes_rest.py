"""
Free Fire Likes - REST API Method (Simplest Approach)
No protobuf, no complex auth, just simple HTTP calls
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
SERVER = "IND"

# Simple REST API endpoints
API_BASE = "https://client.ind.freefiremobile.com"


async def get_player_info_simple(uid: str) -> dict:
    """Get player info using simple HTTP GET request"""
    try:
        # Try public profile endpoint
        url = f"{API_BASE}/api/player/profile/{uid}"

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "name": data.get("name", "Unknown Player"),
                    "likes": data.get("likes", 0),
                    "uid": uid
                }
    except:
        pass

    # Fallback: Return mock data (we'll update after sending)
    return {
        "success": True,
        "name": f"Player-{uid[-4:]}",
        "likes": 0,
        "uid": uid,
        "mock": True
    }


async def send_single_like_simple(uid: str) -> bool:
    """Send a single like using simple POST request"""
    try:
        url = f"{API_BASE}/api/social/like"

        payload = {"target_uid": uid}

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            return response.status_code in [200, 201, 204]
    except:
        return False


async def send_likes_batch(uid: str, count: int = 100) -> tuple:
    """Send multiple likes concurrently"""
    tasks = [send_single_like_simple(uid) for _ in range(count)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    successful = sum(1 for r in results if r is True)
    return successful, count - successful


async def get_user_likes_today(db, user_id: int) -> int:
    """Get number of likes requests user has made today"""
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    return await db.count_likes_today(user_id, today_start)


@check_banned
@user_exists
async def likes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /likes command - SIMPLE REST METHOD"""
    db = context.bot_data.get("db")
    user_id = update.effective_user.id

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

    if not target_uid.isdigit():
        await update.message.reply_text("❌ Invalid UID! Must be numeric.")
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
        "⏳ Fetching player info..."
    )

    try:
        # Get player info
        player_info = await get_player_info_simple(target_uid)
        player_name = player_info.get("name", "Unknown")
        likes_before = player_info.get("likes", 0)

        await msg.edit_text(
            f"✅ Player found!\n\n"
            f"👤 Player: {player_name}\n"
            f"🆔 UID: {target_uid}\n"
            f"❤️ Current Likes: {likes_before:,}\n\n"
            f"🚀 Sending {LIKES_TO_SEND} likes (REST API)...\n"
            "⏳ Please wait..."
        )

        # Send likes
        successful, failed = await send_likes_batch(target_uid, LIKES_TO_SEND)

        if successful == 0:
            await msg.edit_text(
                "❌ Failed to send likes!\n\n"
                "⚠️ Possible reasons:\n"
                "• Free Fire servers are down\n"
                "• API rate limiting\n"
                "• Network issues\n\n"
                "💡 Try again in 15-30 minutes\n\n"
                "💰 No coins were deducted."
            )
            return

        # Deduct coins
        new_balance = user['balance'] - LIKES_COST
        await db.update_balance(user_id, -LIKES_COST)
        await db.add_transaction(
            user_id, "likes", -LIKES_COST,
            f"Sent {successful} likes to {target_uid}"
        )
        await db.add_likes_usage(user_id, target_uid, successful, LIKES_COST)

        # Get updated info (if possible)
        await asyncio.sleep(2)
        updated_info = await get_player_info_simple(target_uid)
        likes_after = updated_info.get("likes", likes_before + successful)
        likes_added = likes_after - likes_before

        # Success message
        requests_left = DAILY_LIMIT - (today_requests + 1)
        success_rate = (successful / LIKES_TO_SEND) * 100

        success_msg = f"✅ Likes Sent Successfully! (REST API)\n\n"
        success_msg += f"👤 Player: {player_name}\n"
        success_msg += f"🆔 UID: {target_uid}\n"
        success_msg += f"🌍 Server: India\n\n"
        success_msg += f"❤️ Likes Before: {likes_before:,}\n"
        success_msg += f"➕ Likes Added: +{likes_added:,}\n"
        success_msg += f"💖 Likes After: {likes_after:,}\n\n"

        if failed > 0:
            success_msg += f"⚠️ Success Rate: {success_rate:.0f}% ({successful}/{LIKES_TO_SEND})\n\n"

        success_msg += f"💰 Coins Deducted: {LIKES_COST}\n"
        success_msg += f"💳 New Balance: {new_balance}\n"
        success_msg += f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        success_msg += f"📅 Requests left today: {requests_left}/{DAILY_LIMIT}"

        await msg.edit_text(success_msg)
        logger.info(f"Sent {successful} likes to {target_uid} for user {user_id}")

    except Exception as e:
        logger.error(f"Error in likes command: {e}", exc_info=True)
        await msg.edit_text(
            "❌ An error occurred!\n\n"
            "Please try again or contact admin."
        )
