"""
Free Fire likes command handlers for RepotechBot
Handles /likes, /likestatus, and /likehistory commands
"""

from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import check_banned, user_exists
from database import get_db
import logging
import sys
import os
from datetime import datetime, timedelta
import asyncio

# Add freefire directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'freefire'))

from count_likes import GetAccountInformation
from get_jwt import create_jwt as get_guest_jwt
from encrypt_like_body import create_like_payload
import httpx
import binascii
import json

logger = logging.getLogger(__name__)

# Constants
LIKES_COST = 50  # Coins per like request
LIKES_TO_SEND = 100  # Number of likes to send per request
MAX_CONCURRENT = 20  # Concurrent requests
DAILY_LIMIT = 3  # Max requests per user per day
SERVER = "IND"  # Only support IND server
BASE_URL = "https://client.ind.freefiremobile.com"

# Load guest accounts
GUESTS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'freefire', 'guests_manager', 'guests_converted.json')


async def load_guest_accounts():
    """Load guest accounts from JSON file"""
    try:
        with open(GUESTS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load guest accounts: {e}")
        return []


async def get_user_likes_today(user_id: int) -> int:
    """Get number of like requests user made today"""
    db = await get_db()
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    cursor = await db.execute(
        "SELECT COUNT(*) FROM likes_usage WHERE user_id = ? AND timestamp >= ?",
        (user_id, today_start.isoformat())
    )
    row = await cursor.fetchone()
    return row[0] if row else 0


async def send_like_with_guest(guest: dict, target_uid: str, semaphore: asyncio.Semaphore) -> bool:
    """Send a like using a guest account"""
    guest_uid = str(guest["uid"])
    guest_pass = guest["password"]

    async with semaphore:
        try:
            # Get JWT token for this guest
            jwt, region, server_url = await get_guest_jwt(guest_uid, guest_pass)

            # Create encrypted like payload
            payload = create_like_payload(target_uid, region)
            if isinstance(payload, str):
                payload = binascii.unhexlify(payload)

            headers = {
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 14; Pixel 8 Build/UP1A.231005.007)",
                "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip",
                "Content-Type": "application/octet-stream",
                "Expect": "100-continue",
                "Authorization": f"Bearer {jwt}",
                "X-Unity-Version": "2018.4.11f1",
                "X-GA": "v1 1",
                "ReleaseVersion": "OB50",
            }

            async with httpx.AsyncClient() as client:
                url = f"{BASE_URL}/LikeProfile"
                response = await client.post(url, data=payload, headers=headers, timeout=30)
                response.raise_for_status()

            logger.info(f"[{guest_uid}] Like sent to {target_uid}! Status: {response.status_code}")
            return True

        except Exception as e:
            logger.error(f"[{guest_uid}] Error sending like: {e}")
            return False


@check_banned
@user_exists
async def likes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /likes <uid> command - Send likes to Free Fire IND server UID"""
    user_id = update.effective_user.id

    # Check if UID was provided
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "❌ Please provide a Free Fire UID!\n\n"
            "📝 Usage: /likes <uid>\n"
            "Example: /likes 1234567890\n\n"
            f"💰 Cost: {LIKES_COST} coins\n"
            f"❤️ Likes sent: {LIKES_TO_SEND}\n"
            f"📅 Daily limit: {DAILY_LIMIT} requests per day"
        )
        return

    target_uid = context.args[0].strip()

    # Validate UID format (should be numeric)
    if not target_uid.isdigit():
        await update.message.reply_text("❌ Invalid UID! UID must be numeric.")
        return

    db = await get_db()

    # Check user balance
    cursor = await db.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    user_data = await cursor.fetchone()

    if not user_data or user_data[0] < LIKES_COST:
        await update.message.reply_text(
            f"❌ Insufficient balance!\n\n"
            f"💰 Required: {LIKES_COST} coins\n"
            f"💳 Your balance: {user_data[0] if user_data else 0} coins\n\n"
            "Use /buy to purchase coins."
        )
        return

    # Check daily limit
    today_requests = await get_user_likes_today(user_id)
    if today_requests >= DAILY_LIMIT:
        await update.message.reply_text(
            f"❌ Daily limit reached!\n\n"
            f"📅 You've used {today_requests}/{DAILY_LIMIT} requests today.\n"
            "⏰ Try again tomorrow!"
        )
        return

    # Send processing message
    processing_msg = await update.message.reply_text(
        "🔄 Processing your request...\n"
        f"🎯 Target UID: {target_uid}\n"
        "⏳ Fetching player information..."
    )

    try:
        # Fetch player info BEFORE sending likes
        endpoint = "/GetPlayerPersonalShow"
        player_info = await GetAccountInformation(target_uid, "0", SERVER, endpoint)

        if player_info.get("error"):
            await processing_msg.edit_text(
                f"❌ Error fetching player info!\n\n"
                f"Message: {player_info.get('message', 'Unknown error')}\n\n"
                "Please check the UID and try again."
            )
            return

        # Extract player information
        basic_info = player_info.get("basicInfo", {})
        player_name = basic_info.get("nickname", "Unknown")
        likes_before = basic_info.get("liked", 0)

        await processing_msg.edit_text(
            f"✅ Player found!\n\n"
            f"👤 Player: {player_name}\n"
            f"🆔 UID: {target_uid}\n"
            f"❤️ Current Likes: {likes_before:,}\n\n"
            f"🚀 Sending {LIKES_TO_SEND} likes...\n"
            "⏳ This may take a moment..."
        )

        # Load guest accounts
        guests = await load_guest_accounts()
        if not guests:
            await processing_msg.edit_text("❌ Error: Guest accounts not available. Please contact admin.")
            return

        # Select guests to use (up to LIKES_TO_SEND)
        guests_to_use = guests[:min(LIKES_TO_SEND, len(guests))]

        # Send likes concurrently
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        tasks = [send_like_with_guest(guest, target_uid, semaphore) for guest in guests_to_use]
        results = await asyncio.gather(*tasks)

        # Count successes
        successful_likes = sum(1 for r in results if r)

        if successful_likes == 0:
            await processing_msg.edit_text(
                "❌ Failed to send likes!\n\n"
                "Please try again later or contact admin."
            )
            return

        # Fetch player info AFTER sending likes to get updated count
        await asyncio.sleep(2)  # Small delay to ensure likes are registered
        player_info_after = await GetAccountInformation(target_uid, "0", SERVER, endpoint)
        basic_info_after = player_info_after.get("basicInfo", {})
        likes_after = basic_info_after.get("liked", likes_before)

        # Calculate actual likes added
        likes_added = likes_after - likes_before

        # Deduct coins ONLY after successful send
        new_balance = user_data[0] - LIKES_COST
        await db.execute(
            "UPDATE users SET balance = ? WHERE user_id = ?",
            (new_balance, user_id)
        )

        # Record transaction
        await db.execute(
            "INSERT INTO transactions (user_id, type, amount, description, timestamp) VALUES (?, ?, ?, ?, ?)",
            (user_id, "likes", -LIKES_COST, f"Sent {successful_likes} likes to UID {target_uid}", datetime.now().isoformat())
        )

        # Record likes usage
        await db.execute(
            "INSERT INTO likes_usage (user_id, uid, likes_sent, coins_spent, timestamp) VALUES (?, ?, ?, ?, ?)",
            (user_id, target_uid, successful_likes, LIKES_COST, datetime.now().isoformat())
        )

        await db.commit()

        # Send success message
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        requests_left = DAILY_LIMIT - (today_requests + 1)

        await processing_msg.edit_text(
            "✅ Likes Sent Successfully!\n\n"
            f"👤 Player: {player_name}\n"
            f"🆔 UID: {target_uid}\n"
            f"🌍 Server: India\n\n"
            f"❤️ Likes Before: {likes_before:,}\n"
            f"➕ Likes Added: +{likes_added:,}\n"
            f"💖 Likes After: {likes_after:,}\n\n"
            f"💰 Coins Deducted: {LIKES_COST}\n"
            f"💳 New Balance: {new_balance}\n"
            f"⏰ Time: {current_time}\n\n"
            f"📅 Requests left today: {requests_left}/{DAILY_LIMIT}"
        )

        logger.info(f"User {user_id} sent {successful_likes} likes to {target_uid}")

    except Exception as e:
        logger.error(f"Error in likes command: {e}")
        await processing_msg.edit_text(
            "❌ An error occurred while processing your request!\n\n"
            "Please try again later or contact admin."
        )


@check_banned
@user_exists
async def likestatus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /likestatus command - Show remaining likes for today"""
    user_id = update.effective_user.id

    # Get today's usage
    today_requests = await get_user_likes_today(user_id)
    requests_left = DAILY_LIMIT - today_requests

    # Calculate time until reset
    now = datetime.now()
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    time_until_reset = tomorrow - now
    hours = int(time_until_reset.total_seconds() // 3600)
    minutes = int((time_until_reset.total_seconds() % 3600) // 60)

    await update.message.reply_text(
        "📊 Free Fire Likes Status\n\n"
        f"📅 Requests used today: {today_requests}/{DAILY_LIMIT}\n"
        f"✅ Requests remaining: {requests_left}/{DAILY_LIMIT}\n\n"
        f"❤️ Likes per request: {LIKES_TO_SEND}\n"
        f"💰 Cost per request: {LIKES_COST} coins\n"
        f"🌍 Server: India (IND)\n\n"
        f"⏰ Reset in: {hours}h {minutes}m\n\n"
        "📝 Use /likes <uid> to send likes!"
    )


@check_banned
@user_exists
async def likehistory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /likehistory command - Show last 5 like requests"""
    user_id = update.effective_user.id
    db = await get_db()

    cursor = await db.execute(
        "SELECT uid, likes_sent, coins_spent, timestamp FROM likes_usage "
        "WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5",
        (user_id,)
    )
    history = await cursor.fetchall()

    if not history:
        await update.message.reply_text(
            "📜 Free Fire Likes History\n\n"
            "No like requests found.\n\n"
            "📝 Use /likes <uid> to send your first likes!"
        )
        return

    # Build history message
    message = "📜 Free Fire Likes History\n\n"
    message += "Last 5 requests:\n\n"

    for i, (uid, likes_sent, coins_spent, timestamp) in enumerate(history, 1):
        # Parse timestamp
        dt = datetime.fromisoformat(timestamp)
        time_str = dt.strftime("%Y-%m-%d %H:%M")

        message += f"{i}. 🆔 UID: {uid}\n"
        message += f"   ❤️ Likes: {likes_sent} | 💰 Cost: {coins_spent} coins\n"
        message += f"   ⏰ {time_str}\n\n"

    message += "📝 Use /likes <uid> to send more likes!"

    await update.message.reply_text(message)
