"""
Free Fire likes command handlers - SIMPLIFIED VERSION
Uses direct API calls without auth server
"""

from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import check_banned, user_exists
import logging
import sys
import os
from datetime import datetime, timedelta
import asyncio

# Add freefire directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'freefire'))

from simple_like_sender import send_multiple_likes
from count_likes import GetAccountInformation
import json

logger = logging.getLogger(__name__)

# Constants
LIKES_COST = 50  # Coins per like request
LIKES_TO_SEND = 100  # Number of likes to send per request
MAX_CONCURRENT = 20  # Concurrent requests
DAILY_LIMIT = 3  # Max requests per user per day
SERVER = "IND"  # Only support IND server

# Load guest accounts
def load_guest_accounts_sync():
    """Load guest accounts from JSON file"""
    accounts_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'freefire', 'accounts.json')
    try:
        with open(accounts_file, 'r') as f:
            data = json.load(f)
            return data.get('guest_accounts', [])
    except FileNotFoundError:
        logger.error(f"Guest accounts file not found: {accounts_file}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing guest accounts JSON: {e}")
        return []


async def load_guest_accounts():
    """Async wrapper for loading guest accounts"""
    return load_guest_accounts_sync()


async def get_user_likes_today(db, user_id: int) -> int:
    """Get number of likes requests user has made today"""
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    return await db.count_likes_today(user_id, today_start)


@check_banned
@user_exists
async def likes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /likes <uid> command - Send likes using SIMPLE DIRECT METHOD"""
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
            f"📅 Daily limit: {DAILY_LIMIT} requests per day"
        )
        return

    target_uid = context.args[0].strip()

    # Validate UID format
    if not target_uid.isdigit():
        await update.message.reply_text("❌ Invalid UID! UID must be numeric.")
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
            f"🚀 Sending {LIKES_TO_SEND} likes using DIRECT METHOD...\n"
            "⏳ This may take a moment..."
        )

        # Load guest accounts
        guests = await load_guest_accounts()
        if not guests:
            await processing_msg.edit_text("❌ Error: Guest accounts not available. Please contact admin.")
            return

        # Select guests to use
        guests_to_use = guests[:min(LIKES_TO_SEND, len(guests))]

        # Send likes using SIMPLE DIRECT METHOD
        logger.info(f"Sending {len(guests_to_use)} likes to {target_uid} using direct method")
        successful, errors = await send_multiple_likes(guests_to_use, target_uid, MAX_CONCURRENT, SERVER)

        if successful == 0:
            # Analyze errors
            error_counts = {}
            for error in errors:
                error_counts[error] = error_counts.get(error, 0) + 1

            error_details = "\n".join([f"• {err}: {count}x" for err, count in error_counts.items()])

            await processing_msg.edit_text(
                "❌ Failed to send likes!\n\n"
                "🔍 Error Details:\n"
                f"{error_details}\n\n"
                "⚠️ This is likely due to:\n"
                "• Free Fire server maintenance\n"
                "• Temporary API unavailability\n"
                "• Rate limiting\n\n"
                "💡 Try again in 10-30 minutes\n\n"
                "💰 No coins were deducted."
            )
            return

        # Fetch player info AFTER sending likes
        await asyncio.sleep(2)
        player_info_after = await GetAccountInformation(target_uid, "0", SERVER, endpoint)
        basic_info_after = player_info_after.get("basicInfo", {})
        likes_after = basic_info_after.get("liked", likes_before)

        # Calculate actual likes added
        likes_added = likes_after - likes_before

        # Deduct coins ONLY after successful send
        new_balance = user['balance'] - LIKES_COST
        await db.update_balance(user_id, -LIKES_COST)

        # Record transaction
        await db.add_transaction(
            user_id, "likes", -LIKES_COST,
            f"Sent {successful} likes to UID {target_uid}"
        )

        # Record likes usage
        await db.add_likes_usage(user_id, target_uid, successful, LIKES_COST)

        # Send success message
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        requests_left = DAILY_LIMIT - (today_requests + 1)

        # Calculate success rate
        failed = len(guests_to_use) - successful
        success_rate = (successful / len(guests_to_use)) * 100 if guests_to_use else 0

        success_msg = "✅ Likes Sent Successfully! (DIRECT METHOD)\n\n"
        success_msg += f"👤 Player: {player_name}\n"
        success_msg += f"🆔 UID: {target_uid}\n"
        success_msg += f"🌍 Server: India\n\n"
        success_msg += f"❤️ Likes Before: {likes_before:,}\n"
        success_msg += f"➕ Likes Added: +{likes_added:,}\n"
        success_msg += f"💖 Likes After: {likes_after:,}\n\n"

        # Show partial success warning if applicable
        if failed > 0:
            success_msg += f"⚠️ Success Rate: {success_rate:.0f}% ({successful}/{len(guests_to_use)})\n"
            success_msg += f"ℹ️ {failed} accounts failed (server issues)\n\n"

        success_msg += f"💰 Coins Deducted: {LIKES_COST}\n"
        success_msg += f"💳 New Balance: {new_balance}\n"
        success_msg += f"⏰ Time: {current_time}\n\n"
        success_msg += f"📅 Requests left today: {requests_left}/{DAILY_LIMIT}"

        await processing_msg.edit_text(success_msg)

        logger.info(f"Successfully sent {successful}/{len(guests_to_use)} likes to {target_uid} for user {user_id}")

    except Exception as e:
        logger.error(f"Error in likes command: {e}", exc_info=True)
        await processing_msg.edit_text(
            "❌ An error occurred while processing your request!\n\n"
            "Please try again later or contact admin."
        )
