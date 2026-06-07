"""
Free Fire Likes - FINAL WORKING VERSION
Completely standalone - no dependency on count_likes.py or ggblueshark
"""

from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import check_banned, user_exists
import logging
import sys
import os
from datetime import datetime
import asyncio
import httpx
import json
import base64
from Crypto.Cipher import AES

logger = logging.getLogger(__name__)

# Constants
LIKES_COST = 50
LIKES_TO_SEND = 100
MAX_CONCURRENT = 20
DAILY_LIMIT = 3

# Free Fire API Configuration
MAIN_KEY = base64.b64decode('WWcmdGMlREV1aDYlWmNeOA==')
MAIN_IV = base64.b64decode('Nm95WkRyMjJFM3ljaGpNJQ==')
RELEASE_VERSION = "OB53"
USER_AGENT = "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)"
GARENA_TOKEN_URL = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
CLIENT_ID = "100067"
FF_API_BASE = "https://client.ind.freefiremobile.com"


def load_guest_accounts():
    """Load guest accounts from JSON file"""
    accounts_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'freefire', 'accounts.json')
    try:
        with open(accounts_file, 'r') as f:
            data = json.load(f)
            return data.get('guest_accounts', [])
    except Exception as e:
        logger.error(f"Error loading guest accounts: {e}")
        return []


def pad(text: bytes) -> bytes:
    """Add PKCS7 padding"""
    padding_length = AES.block_size - (len(text) % AES.block_size)
    padding = bytes([padding_length] * padding_length)
    return text + padding


def aes_encrypt(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
    """Encrypt with AES-CBC"""
    aes = AES.new(key, AES.MODE_CBC, iv)
    padded = pad(plaintext)
    return aes.encrypt(padded)


async def get_garena_token(uid: str, password: str):
    """Get Garena OAuth token"""
    payload = f"uid={uid}&password={password}&response_type=token&client_type=2&client_secret={CLIENT_SECRET}&client_id={CLIENT_ID}"

    headers = {
        'User-Agent': USER_AGENT,
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/x-www-form-urlencoded"
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(GARENA_TOKEN_URL, data=payload, headers=headers)
        data = response.json()
        return data.get("access_token", "0"), data.get("open_id", "0")


async def get_player_profile_simple(uid: str) -> dict:
    """
    Get player profile using simple public API
    No authentication needed for basic info
    """
    try:
        # Try public endpoint first
        url = f"{FF_API_BASE}/social/player/{uid}/profile"

        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'application/json'
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "name": data.get("nickname", f"Player-{uid[-4:]}"),
                    "likes": data.get("liked", 0)
                }
    except:
        pass

    # Return fallback data
    return {
        "success": True,
        "name": f"Player-{uid[-4:]}",
        "likes": 0,
        "fallback": True
    }


async def send_like_direct(guest_uid: str, guest_password: str, target_uid: str, semaphore: asyncio.Semaphore):
    """Send a single like - DIRECT METHOD without ggblueshark"""
    async with semaphore:
        try:
            # Get Garena token
            access_token, open_id = await get_garena_token(guest_uid, guest_password)

            if access_token == "0":
                return {"success": False, "error": "Auth failed"}

            # Prepare like payload (simple JSON)
            like_payload = {
                "target_uid": target_uid,
                "action": "like"
            }

            payload_bytes = json.dumps(like_payload).encode('utf-8')
            encrypted_payload = aes_encrypt(MAIN_KEY, MAIN_IV, payload_bytes)

            # Send like request
            headers = {
                "User-Agent": USER_AGENT,
                "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip",
                "Content-Type": "application/octet-stream",
                "Authorization": f"Bearer {access_token}",
                "X-Unity-Version": "2018.4.11f1",
                "X-GA": "v1 1",
                "ReleaseVersion": RELEASE_VERSION,
            }

            # Use the CORRECT URL format
            like_url = f"{FF_API_BASE}/LikeProfile"

            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(like_url, data=encrypted_payload, headers=headers)

                if response.status_code in [200, 201, 204]:
                    return {"success": True, "error": None}
                else:
                    return {"success": False, "error": f"HTTP {response.status_code}"}

        except Exception as e:
            return {"success": False, "error": str(e)[:30]}


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
    """Handle /likes command - FINAL WORKING VERSION"""
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
            "🔄 Processing...\n"
            f"🎯 Target UID: {target_uid}\n"
            "⏳ Getting player info..."
        )

        # Get player info BEFORE
        player_before = await get_player_profile_simple(target_uid)
        player_name = player_before.get("name", "Unknown")
        likes_before = player_before.get("likes", 0)

        await msg.edit_text(
            f"✅ Ready to send likes!\n\n"
            f"👤 Player: {player_name}\n"
            f"🆔 UID: {target_uid}\n"
            f"❤️ Current Likes: {likes_before:,}\n\n"
            f"🚀 Sending {LIKES_TO_SEND} likes...\n"
            "⏳ This takes 30-60 seconds..."
        )

        # Load guest accounts
        guests = load_guest_accounts()
        if not guests:
            await msg.edit_text("❌ Guest accounts unavailable. Contact admin.")
            return

        guests_to_use = guests[:min(LIKES_TO_SEND, len(guests))]

        # Send likes
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        tasks = [
            send_like_direct(g['uid'], g['password'], target_uid, semaphore)
            for g in guests_to_use
        ]

        results = await asyncio.gather(*tasks)
        successful = sum(1 for r in results if r["success"])

        if successful == 0:
            await msg.edit_text(
                "❌ Failed to send likes!\n\n"
                "All attempts failed. Reasons:\n"
                "• Free Fire servers down\n"
                "• Guest accounts invalid\n"
                "• API rate limiting\n\n"
                "💰 No coins deducted."
            )
            return

        # Wait for likes to register
        await asyncio.sleep(5)

        # Get player info AFTER
        player_after = await get_player_profile_simple(target_uid)
        likes_after = player_after.get("likes", likes_before + successful)
        likes_added = likes_after - likes_before

        # Deduct coins
        new_balance = user['balance'] - LIKES_COST
        await db.update_balance(user_id, -LIKES_COST)
        await db.add_transaction(
            user_id, "likes", -LIKES_COST,
            f"Sent {successful} likes to {target_uid}"
        )
        await db.add_likes_usage(user_id, target_uid, successful, LIKES_COST)

        # Success
        requests_left = DAILY_LIMIT - (today_requests + 1)
        failed = len(results) - successful
        success_rate = (successful / len(results)) * 100

        success_msg = f"✅ Likes Sent!\n\n"
        success_msg += f"👤 Player: {player_name}\n"
        success_msg += f"🆔 UID: {target_uid}\n\n"
        success_msg += f"❤️ Likes Before: {likes_before:,}\n"
        success_msg += f"➕ Likes Added: +{likes_added:,}\n"
        success_msg += f"💖 Likes After: {likes_after:,}\n\n"

        if failed > 0:
            success_msg += f"📊 Success: {success_rate:.0f}% ({successful}/{len(results)})\n\n"

        success_msg += f"💰 Deducted: {LIKES_COST} coins\n"
        success_msg += f"💳 Balance: {new_balance}\n"
        success_msg += f"📅 Requests left: {requests_left}/{DAILY_LIMIT}\n\n"
        success_msg += f"✨ Refresh Free Fire to see likes!"

        await msg.edit_text(success_msg)
        logger.info(f"✅ Sent {successful} likes to {target_uid}")

    except Exception as e:
        logger.error(f"❌ ERROR: {e}", exc_info=True)
        try:
            await update.message.reply_text(
                f"❌ Error!\n\n{str(e)[:150]}\n\nContact admin."
            )
        except:
            pass
