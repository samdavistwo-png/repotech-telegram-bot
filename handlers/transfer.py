"""
Transfer command handler for RepotechBot
Handles /transfer command
"""

from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import check_banned, user_exists
from utils.helpers import validate_user_id, validate_amount
import logging

logger = logging.getLogger(__name__)


@check_banned
@user_exists
async def transfer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /transfer command"""
    db = context.bot_data.get("db")
    sender_id = update.effective_user.id

    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ Usage: /transfer <user_id> <amount>\n\n"
            "Example: /transfer 123456789 50\n\n"
            "💡 Transfer coins to another user"
        )
        return

    # Validate recipient and amount
    recipient_id = validate_user_id(context.args[0])
    amount = validate_amount(context.args[1])

    if not recipient_id or not amount:
        await update.message.reply_text("❌ Invalid user ID or amount")
        return

    # Check if sender is trying to transfer to themselves
    if sender_id == recipient_id:
        await update.message.reply_text("❌ You cannot transfer coins to yourself!")
        return

    # Check if recipient exists
    recipient = await db.get_user(recipient_id)
    if not recipient:
        await update.message.reply_text(
            "❌ Recipient not found!\n\n"
            "The user must have started the bot first."
        )
        return

    # Check if recipient is banned
    if recipient["is_banned"]:
        await update.message.reply_text("❌ Cannot transfer to a banned user")
        return

    # Get sender balance
    sender = await db.get_user(sender_id)

    # Check if sender has enough balance
    if sender["balance"] < amount:
        await update.message.reply_text(
            f"❌ Insufficient balance!\n\n"
            f"💰 Your balance: {sender['balance']:,} coins\n"
            f"💸 Transfer amount: {amount:,} coins\n"
            f"📉 Shortage: {amount - sender['balance']:,} coins"
        )
        return

    # Perform transfer
    await db.update_balance(sender_id, -amount)
    await db.add_transaction(
        sender_id, "transfer_out", amount, f"Transfer to user {recipient_id}"
    )

    await db.update_balance(recipient_id, amount)
    await db.add_transaction(
        recipient_id, "transfer_in", amount, f"Transfer from user {sender_id}"
    )

    # Get updated balances
    updated_sender = await db.get_user(sender_id)
    updated_recipient = await db.get_user(recipient_id)

    # Confirm to sender
    await update.message.reply_text(
        f"✅ Transfer Successful!\n\n"
        f"💸 Sent: {amount:,} coins\n"
        f"👤 To: @{recipient['username'] or recipient_id}\n"
        f"💰 Your new balance: {updated_sender['balance']:,} coins"
    )

    # Notify recipient
    try:
        await context.bot.send_message(
            chat_id=recipient_id,
            text=f"💰 You received a transfer!\n\n"
            f"📥 Received: {amount:,} coins\n"
            f"👤 From: @{sender['username'] or sender_id}\n"
            f"💵 Your new balance: {updated_recipient['balance']:,} coins"
        )
    except Exception as e:
        logger.error(f"Failed to notify recipient {recipient_id}: {e}")

    logger.info(f"User {sender_id} transferred {amount} coins to {recipient_id}")
