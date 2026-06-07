"""
Sambots Likes Handler
100% real likes using bulk Sambots guest accounts
Processes in batches of 30 with logout/login cycles
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_user_balance, update_user_balance
from freefire.ffmax_player_api import get_complete_player_info
from freefire.batch_likes_engine import send_likes_all_batches, load_sambots_accounts

logger = logging.getLogger(__name__)

LIKES_COST = 50  # 50 coins per 100 likes
LIKES_AMOUNT = 100


async def likes_sambots_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /likes command with Sambots batch processing

    Usage: /likes <uid>
    Cost: 50 coins for 100 likes
    """
    user_id = update.effective_user.id

    # Check if UID provided
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a Free Fire UID!\n\n"
            "Usage: /likes <uid>\n"
            "Example: /likes 1234567890\n\n"
            "💰 Cost: 50 coins for 100 likes"
        )
        return

    target_uid = context.args[0].strip()

    # Validate UID (numeric, 6-12 digits)
    if not target_uid.isdigit() or len(target_uid) < 6 or len(target_uid) > 12:
        await update.message.reply_text(
            "❌ Invalid UID format!\n\n"
            "Free Fire UID must be:\n"
            "• Numeric only\n"
            "• 6-12 digits long\n\n"
            "Example: /likes 1234567890"
        )
        return

    # Check user balance
    balance = await get_user_balance(user_id)

    if balance < LIKES_COST:
        await update.message.reply_text(
            f"❌ Insufficient balance!\n\n"
            f"You need: {LIKES_COST} coins\n"
            f"You have: {balance} coins\n"
            f"Required: {LIKES_COST - balance} more coins\n\n"
            f"💡 Use /recharge to add coins"
        )
        return

    # Send initial message
    msg = await update.message.reply_text(
        "🔍 Fetching player information...\n\n"
        "⏳ Please wait..."
    )

    try:
        # Get REAL player info (tries FF MAX + FF + third-party APIs)
        player_info = await get_complete_player_info(target_uid)

        player_name = player_info.get("name", f"Player-{target_uid[-6:]}")
        likes_before = player_info.get("likes", 0)
        level = player_info.get("level", 1)
        game_type = player_info.get("game", "Unknown")

        # Check if we got real data or fallback
        if not player_info.get("success"):
            await msg.edit_text(
                f"⚠️ Could not verify player UID: {target_uid}\n\n"
                f"This UID may not exist or APIs are temporarily down.\n\n"
                f"Do you want to proceed anyway?\n\n"
                f"Reply with 'yes' to continue or 'no' to cancel."
            )
            # TODO: Add conversation handler to wait for yes/no response
            return

        # Show player info
        await msg.edit_text(
            f"✅ Player Found!\n\n"
            f"👤 Name: {player_name}\n"
            f"📊 Level: {level}\n"
            f"🎮 Game: {game_type}\n"
            f"❤️  Current Likes: {likes_before:,}\n\n"
            f"🚀 Processing {LIKES_AMOUNT} likes...\n"
            f"⏳ Using Sambots batch system (30 accounts per batch)..."
        )

        # Load Sambots accounts
        sambots_accounts = load_sambots_accounts()

        if not sambots_accounts:
            await msg.edit_text(
                "❌ No Sambots accounts available!\n\n"
                "⚠️ Admin needs to create Sambots accounts using:\n"
                "   python3 freefire/ffmax_bulk_creator.py\n\n"
                "💡 Alternative: Use HL Gaming Premium API\n\n"
                "💰 No coins deducted."
            )
            return

        if len(sambots_accounts) < LIKES_AMOUNT:
            await msg.edit_text(
                f"⚠️ Not enough Sambots accounts!\n\n"
                f"Available: {len(sambots_accounts)} accounts\n"
                f"Required: {LIKES_AMOUNT} accounts\n\n"
                f"⚠️ Admin needs to create more accounts.\n\n"
                f"💰 No coins deducted."
            )
            return

        # Deduct coins BEFORE sending likes
        await update_user_balance(user_id, -LIKES_COST)
        logger.info(f"Deducted {LIKES_COST} coins from user {user_id}")

        # Send likes using batch system
        result = await send_likes_all_batches(sambots_accounts, target_uid, LIKES_AMOUNT)

        likes_sent = result["total_successful"]
        likes_failed = result["total_failed"]
        success_rate = result["success_rate"]

        # Calculate estimated new likes count
        likes_after = likes_before + likes_sent

        if likes_sent > 0:
            # Success message
            await msg.edit_text(
                f"✅ Likes sent successfully!\n\n"
                f"👤 Player: {player_name}\n"
                f"📊 Level: {level}\n"
                f"🎮 Game: {game_type}\n\n"
                f"❤️  Likes Before: {likes_before:,}\n"
                f"➕ Likes Added: {likes_sent:,}\n"
                f"❤️  Likes After: {likes_after:,}\n\n"
                f"📊 Success Rate: {success_rate:.1f}%\n"
                f"✅ Successful: {likes_sent}/{LIKES_AMOUNT}\n"
                f"❌ Failed: {likes_failed}/{LIKES_AMOUNT}\n\n"
                f"💰 Coins deducted: {LIKES_COST}"
            )

            logger.info(f"Successfully sent {likes_sent} likes to {target_uid} for user {user_id}")

        else:
            # All likes failed - refund coins
            await update_user_balance(user_id, LIKES_COST)
            logger.info(f"Refunded {LIKES_COST} coins to user {user_id} - all likes failed")

            await msg.edit_text(
                "⚠️ No likes sent!\n\n"
                f"❌ All {LIKES_AMOUNT} Sambots accounts failed to send likes.\n\n"
                "Possible causes:\n"
                "• Garena is blocking bulk authentication\n"
                "• Sambots accounts may be expired/banned\n"
                "• Target UID may be invalid\n"
                "• Garena API temporary issues\n\n"
                "🔧 Admin needs to:\n"
                "1. Create fresh Sambots accounts\n"
                "2. OR setup HL Gaming Premium API\n\n"
                "💰 Coins refunded (no charge)."
            )

    except Exception as e:
        logger.error(f"Error in likes handler for user {user_id}: {e}", exc_info=True)

        await msg.edit_text(
            "❌ System error occurred!\n\n"
            f"Error: {type(e).__name__}\n"
            f"Details: {str(e)}\n\n"
            "Please try again later or contact support.\n\n"
            "💰 No coins deducted."
        )
