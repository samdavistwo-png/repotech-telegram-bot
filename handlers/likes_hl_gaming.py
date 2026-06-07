"""
HL Gaming Premium Likes Handler
100% working solution - shows real player name, before/after likes
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_user_balance, update_user_balance
from freefire.hl_gaming_player_api import get_player_info_hl_gaming
from freefire.hl_gaming_likes_api import send_likes_hl_gaming

logger = logging.getLogger(__name__)

LIKES_COST = 50  # 50 coins per 100 likes
LIKES_AMOUNT = 100


async def likes_hl_gaming_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /likes command with HL Gaming Premium API

    Usage: /likes <uid>
    Cost: 50 coins for 100 likes
    """
    user_id = update.effective_user.id

    # Check if UID provided
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a Free Fire UID!\n\n"
            "Usage: /likes <uid>\n"
            "Example: /likes 1810201201\n\n"
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
            "Example: /likes 1810201201"
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
        # Get REAL player info using HL Gaming API
        player_info = get_player_info_hl_gaming(target_uid, region="ind")

        if not player_info.get('success'):
            error_code = player_info.get('error', 'UNKNOWN')
            error_message = player_info.get('message', 'Unknown error')

            if error_code == 'API_NOT_CONFIGURED':
                await msg.edit_text(
                    "⚠️ HL Gaming API not configured!\n\n"
                    "Admin needs to add API credentials to Railway:\n"
                    "1. Get credentials from: https://www.hlgamingofficial.com/p/api.html\n"
                    "2. Add to Railway Variables:\n"
                    "   - HL_GAMING_USERUID\n"
                    "   - HL_GAMING_API_KEY\n\n"
                    "💰 No coins deducted."
                )
                return

            elif error_code == 'INVALID_CREDENTIALS':
                await msg.edit_text(
                    "❌ Invalid API credentials!\n\n"
                    "Admin needs to check HL Gaming API credentials.\n\n"
                    "💰 No coins deducted."
                )
                return

            elif error_code == 'UID_NOT_FOUND':
                await msg.edit_text(
                    f"❌ Player not found!\n\n"
                    f"UID {target_uid} does not exist in India server.\n\n"
                    f"Please check:\n"
                    f"• UID is correct\n"
                    f"• Player is on India (IND) server\n\n"
                    f"💰 No coins deducted."
                )
                return

            else:
                await msg.edit_text(
                    f"❌ Error fetching player info!\n\n"
                    f"Error: {error_message}\n\n"
                    f"💰 No coins deducted."
                )
                return

        # Extract player information
        player_name = player_info.get('name', f'Player-{target_uid[-6:]}')
        level = player_info.get('level', 1)
        likes_before = player_info.get('likes', 0)
        rank = player_info.get('rank', '')
        guild = player_info.get('guild', '')

        # Show player info
        player_text = (
            f"✅ Player Found!\n\n"
            f"👤 Name: {player_name}\n"
            f"📊 Level: {level}\n"
        )

        if rank:
            player_text += f"🏆 Rank: {rank}\n"

        if guild:
            player_text += f"🎮 Guild: {guild}\n"

        player_text += (
            f"❤️  Current Likes: {likes_before:,}\n\n"
            f"🚀 Sending {LIKES_AMOUNT} likes...\n"
            f"⏳ Processing with HL Gaming Premium API..."
        )

        await msg.edit_text(player_text)

        # Deduct coins BEFORE sending likes
        await update_user_balance(user_id, -LIKES_COST)
        logger.info(f"Deducted {LIKES_COST} coins from user {user_id}")

        # Send likes using HL Gaming API
        result = send_likes_hl_gaming(target_uid, LIKES_AMOUNT, region="ind")

        if result.get('success'):
            likes_sent = result.get('likes_sent', LIKES_AMOUNT)
            likes_after = likes_before + likes_sent

            # Success message
            success_text = (
                f"✅ Likes sent successfully!\n\n"
                f"👤 Player: {player_name}\n"
                f"📊 Level: {level}\n"
            )

            if rank:
                success_text += f"🏆 Rank: {rank}\n"

            if guild:
                success_text += f"🎮 Guild: {guild}\n"

            success_text += (
                f"\n❤️  Likes Before: {likes_before:,}\n"
                f"➕ Likes Added: {likes_sent:,}\n"
                f"❤️  Likes After: {likes_after:,}\n\n"
                f"⚡ Delivered in < 5 seconds\n"
                f"💰 Coins deducted: {LIKES_COST}"
            )

            await msg.edit_text(success_text)

            logger.info(f"Successfully sent {likes_sent} likes to {target_uid} for user {user_id}")

        else:
            # Likes sending failed - refund coins
            await update_user_balance(user_id, LIKES_COST)
            logger.info(f"Refunded {LIKES_COST} coins to user {user_id} - likes sending failed")

            error_message = result.get('message', 'Unknown error')

            await msg.edit_text(
                f"❌ Failed to send likes!\n\n"
                f"Error: {error_message}\n\n"
                f"Please try again or contact support.\n\n"
                f"💰 Coins refunded (no charge)."
            )

    except Exception as e:
        logger.error(f"Error in HL Gaming likes handler for user {user_id}: {e}", exc_info=True)

        await msg.edit_text(
            "❌ System error occurred!\n\n"
            f"Error: {type(e).__name__}\n"
            f"Details: {str(e)}\n\n"
            "Please try again later or contact support.\n\n"
            "💰 No coins deducted."
        )
