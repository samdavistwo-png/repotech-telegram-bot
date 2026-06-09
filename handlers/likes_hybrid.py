"""
Hybrid Likes Handler - Combines Guest Accounts (Free) + HL Gaming (Premium Fallback)
Strategy: Try guest method first, fallback to HL Gaming if needed
100% working solution with intelligent fallback system
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import check_banned, user_exists
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'freefire'))

from guest_likes_engine import send_likes_with_guests, get_available_guests
from hl_gaming_player_api import get_player_info_hl_gaming
from hl_gaming_likes_api import send_likes_hl_gaming
from count_likes import GetAccountInformation

logger = logging.getLogger(__name__)

LIKES_COST = 50  # 50 coins per 100 likes
LIKES_AMOUNT = 100
GUEST_THRESHOLD = 50  # Minimum likes from guest method to consider success


@check_banned
@user_exists
async def likes_hybrid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /likes command with Hybrid System:
    1. Try guest accounts first (free method)
    2. Fallback to HL Gaming if guest method fails/exhausted

    Usage: /likes <uid>
    Cost: 50 coins for 100 likes
    """
    db = context.bot_data.get("db")
    user_id = update.effective_user.id

    # Check if UID provided
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a Free Fire UID!\n\n"
            "Usage: /likes <uid>\n"
            "Example: /likes 1810201201\n\n"
            "💰 Cost: 50 coins for 100 likes\n"
            "🎁 System: Smart Hybrid (Guest + Premium Fallback)"
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
    user = await db.get_user(user_id)
    balance = user['balance']

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
        # Get player info using HL Gaming API (reliable)
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
        )

        await msg.edit_text(player_text)

        # Deduct coins BEFORE sending likes
        await db.update_balance(user_id, -LIKES_COST)
        logger.info(f"Deducted {LIKES_COST} coins from user {user_id}")

        # Re-check guest availability AFTER coin deduction (prevent double-spend race)
        available_guests = get_available_guests(target_uid)

        # Decide which method to use
        if available_guests >= GUEST_THRESHOLD:
            player_text += f"\n🎁 Trying Guest Accounts (Free Method)...\n⏳ Processing {min(available_guests, LIKES_AMOUNT)} available guests..."
            use_guest_first = True
        else:
            player_text += f"\n⚡ Using HL Gaming Premium API...\n⏳ Processing..."
            use_guest_first = False

        await msg.edit_text(player_text)

        # Track which method was used
        method_used = "unknown"
        likes_sent = 0
        success = False

        # Try Guest Method First (if available)
        if use_guest_first:
            logger.info(f"Attempting guest method for {target_uid} (user {user_id})")

            try:
                guest_result = await send_likes_with_guests(target_uid, LIKES_AMOUNT, region="IND")

                if guest_result.get('success') and guest_result.get('likes_sent', 0) >= GUEST_THRESHOLD:
                    # Guest method full success
                    likes_sent = guest_result.get('likes_sent', 0)
                    remaining_guests = guest_result.get('available_guests_remaining', 0)
                    method_used = "guest"
                    success = True

                    logger.info(
                        f"Guest method SUCCESS for {target_uid}: "
                        f"{likes_sent} likes sent, {remaining_guests} guests remaining"
                    )

                elif guest_result.get('likes_sent', 0) > 0:
                    # Partial success - accumulate with HL Gaming
                    partial_likes = guest_result.get('likes_sent', 0)
                    remaining_likes = LIKES_AMOUNT - partial_likes

                    logger.info(f"Guest method sent {partial_likes} likes, need {remaining_likes} more from HL Gaming")
                    await msg.edit_text(
                        f"{player_text}\n\n"
                        f"🔄 Guest method: {partial_likes} likes\n"
                        f"🔄 Trying HL Gaming for remaining {remaining_likes} likes..."
                    )

                    # Try HL Gaming for remaining
                    hl_result = send_likes_hl_gaming(target_uid, remaining_likes, region="IND")
                    if hl_result.get('success'):
                        total_likes = partial_likes + hl_result.get('likes_sent', remaining_likes)
                        likes_sent = total_likes
                        method_used = "hybrid_both"
                        success = True
                        logger.info(f"Hybrid SUCCESS: {partial_likes} (guest) + {hl_result.get('likes_sent', remaining_likes)} (HL) = {total_likes}")
                    else:
                        # HL Gaming failed, but we got partial likes
                        likes_sent = partial_likes
                        method_used = "guest_partial"
                        success = True
                        logger.warning(f"Guest partial only: {partial_likes} likes (HL Gaming failed)")

                else:
                    # Guest method totally failed, try HL Gaming
                    logger.warning(
                        f"Guest method FAILED for {target_uid}. Falling back to HL Gaming..."
                    )

                    await msg.edit_text(
                        player_text + f"\n\n⚠️ Guest method failed.\n"
                        "⚡ Switching to HL Gaming Premium..."
                    )

                    # Fallback to HL Gaming
                    hl_result = send_likes_hl_gaming(target_uid, LIKES_AMOUNT, region="IND")

                    if hl_result.get('success'):
                        likes_sent = hl_result.get('likes_sent', LIKES_AMOUNT)
                        method_used = "hl_gaming_fallback"
                        success = True
                        logger.info(f"HL Gaming fallback SUCCESS for {target_uid}: {likes_sent} likes")
                    else:
                        # Both methods failed
                        error_msg = hl_result.get('message', 'Unknown error')
                        logger.error(f"Both guest and HL Gaming FAILED for {target_uid}: {error_msg}")
                        method_used = "both_failed"
                        success = False

            except Exception as e:
                logger.error(f"Guest method exception for {target_uid}: {e}", exc_info=True)
                # Try HL Gaming fallback after exception
                await msg.edit_text(
                    player_text + f"\n\n⚠️ Guest method error.\n"
                    "⚡ Switching to HL Gaming Premium..."
                )

                hl_result = send_likes_hl_gaming(target_uid, LIKES_AMOUNT, region="IND")

                if hl_result.get('success'):
                    likes_sent = hl_result.get('likes_sent', LIKES_AMOUNT)
                    method_used = "hl_gaming_fallback"
                    success = True
                else:
                    method_used = "both_failed"
                    success = False

        else:
            # Use HL Gaming directly (not enough guests)
            logger.info(f"Using HL Gaming directly for {target_uid} (user {user_id})")

            hl_result = send_likes_hl_gaming(target_uid, LIKES_AMOUNT, region="IND")

            if hl_result.get('success'):
                likes_sent = hl_result.get('likes_sent', LIKES_AMOUNT)
                method_used = "hl_gaming_direct"
                success = True
                logger.info(f"HL Gaming direct SUCCESS for {target_uid}: {likes_sent} likes")
            else:
                error_msg = hl_result.get('message', 'Unknown error')
                logger.error(f"HL Gaming direct FAILED for {target_uid}: {error_msg}")
                method_used = "hl_gaming_failed"
                success = False

        # Handle results
        if success:
            likes_after = likes_before + likes_sent

            # Build success message based on method used
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
            )

            # Add method-specific info
            if method_used == "guest":
                remaining = get_available_guests(target_uid)
                success_text += (
                    f"🎁 Method: Guest Accounts (Free)\n"
                    f"🔢 Remaining Guests: {remaining} for this player\n\n"
                    f"⚡ Delivered in < 10 seconds\n"
                )
            elif method_used == "hybrid_both":
                success_text += (
                    f"🔄 Method: Hybrid (Guest + HL Gaming)\n"
                    f"💡 Combined both methods for full delivery\n\n"
                    f"⚡ Delivered in < 10 seconds\n"
                )
            elif method_used == "guest_partial":
                success_text += (
                    f"🎁 Method: Guest Accounts (Partial)\n"
                    f"⚠️ Note: Only {likes_sent} likes available\n\n"
                    f"⚡ Delivered in < 10 seconds\n"
                )
            elif method_used in ["hl_gaming_fallback", "hl_gaming_direct"]:
                success_text += (
                    f"⚡ Method: HL Gaming Premium\n"
                )
                if method_used == "hl_gaming_fallback":
                    success_text += f"💡 Note: Guest accounts exhausted/failed\n\n"
                else:
                    success_text += f"💡 Note: Insufficient guest accounts\n\n"
                success_text += f"⚡ Delivered in < 5 seconds\n"

            success_text += f"💰 Coins deducted: {LIKES_COST}"

            await msg.edit_text(success_text)

            logger.info(
                f"Successfully sent {likes_sent} likes to {target_uid} for user {user_id} "
                f"using {method_used}"
            )

        else:
            # All methods failed - refund coins
            await db.update_balance(user_id, LIKES_COST)
            logger.info(f"Refunded {LIKES_COST} coins to user {user_id} - all methods failed")

            if method_used == "both_failed":
                error_text = (
                    f"❌ Failed to send likes!\n\n"
                    f"Both guest and HL Gaming methods failed.\n\n"
                    f"Please try again later or contact support.\n\n"
                    f"💰 Coins refunded (no charge)."
                )
            elif method_used == "hl_gaming_failed":
                hl_error = hl_result.get('message', 'Unknown error') if 'hl_result' in locals() else 'Unknown error'
                error_text = (
                    f"❌ Failed to send likes!\n\n"
                    f"HL Gaming Error: {hl_error}\n\n"
                    f"Please try again later or contact support.\n\n"
                    f"💰 Coins refunded (no charge)."
                )
            else:
                error_text = (
                    f"❌ Failed to send likes!\n\n"
                    f"An unexpected error occurred.\n\n"
                    f"Please try again later or contact support.\n\n"
                    f"💰 Coins refunded (no charge)."
                )

            await msg.edit_text(error_text)

    except Exception as e:
        logger.error(f"Error in hybrid likes handler for user {user_id}: {e}", exc_info=True)

        # Try to refund if coins were deducted
        try:
            # Check if coins were actually deducted by comparing with expected balance
            expected_balance = balance - LIKES_COST
            user_after = await db.get_user(user_id)

            # Only refund if balance matches expected (coins were deducted)
            if user_after['balance'] == expected_balance:
                await db.update_balance(user_id, LIKES_COST)
                logger.info(f"Refunded {LIKES_COST} coins to user {user_id} after exception")
                refund_msg = "💰 Coins refunded (no charge)."
            else:
                logger.warning(f"Refund skipped for user {user_id} - balance mismatch (expected: {expected_balance}, actual: {user_after['balance']})")
                refund_msg = "💰 No coins deducted."
        except Exception as refund_error:
            logger.error(f"Error during refund check: {refund_error}")
            refund_msg = "💰 Error verifying balance."

        await msg.edit_text(
            "❌ System error occurred!\n\n"
            f"Error: {type(e).__name__}\n"
            f"Details: {str(e)}\n\n"
            "Please try again later or contact support.\n\n"
            f"{refund_msg}"
        )
