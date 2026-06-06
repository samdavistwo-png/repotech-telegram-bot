"""
Balance command handlers for RepotechBot
Handles /balance, /spend, and /history commands
"""

from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import check_banned, user_exists
from utils.helpers import format_transaction_type, format_datetime, validate_amount
import logging

logger = logging.getLogger(__name__)


@check_banned
@user_exists
async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /balance command"""
    db = context.bot_data.get("db")
    user_id = update.effective_user.id

    user = await db.get_user(user_id)

    await update.message.reply_text(
        f"💰 Your Current Balance\n\n"
        f"👤 User: @{user['username'] or user_id}\n"
        f"💵 Balance: {user['balance']:,} coins\n\n"
        f"Use /buy to purchase more coins!"
    )


@check_banned
@user_exists
async def spend_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /spend command"""
    db = context.bot_data.get("db")
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text(
            "❌ Usage: /spend <amount>\n\n"
            "Example: /spend 50"
        )
        return

    # Validate amount
    amount = validate_amount(context.args[0])
    if not amount:
        await update.message.reply_text("❌ Please enter a valid amount (positive number)")
        return

    # Get user balance
    user = await db.get_user(user_id)

    # Check if user has enough balance
    if user["balance"] < amount:
        await update.message.reply_text(
            f"❌ Insufficient balance!\n\n"
            f"💰 Your balance: {user['balance']:,} coins\n"
            f"💸 Amount to spend: {amount:,} coins\n"
            f"📉 Shortage: {amount - user['balance']:,} coins\n\n"
            f"Use /buy to purchase more coins!"
        )
        return

    # Deduct balance
    await db.update_balance(user_id, -amount)
    await db.add_transaction(user_id, "debit", amount, "Manual spend")

    # Get updated balance
    updated_user = await db.get_user(user_id)

    await update.message.reply_text(
        f"✅ Successfully spent {amount:,} coins!\n\n"
        f"💰 Previous balance: {user['balance']:,} coins\n"
        f"💸 Spent: {amount:,} coins\n"
        f"💵 New balance: {updated_user['balance']:,} coins"
    )

    logger.info(f"User {user_id} spent {amount} coins")


@check_banned
@user_exists
async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /history command"""
    db = context.bot_data.get("db")
    user_id = update.effective_user.id

    transactions = await db.get_transaction_history(user_id, limit=5)

    if not transactions:
        await update.message.reply_text(
            "📜 Transaction History\n\n"
            "No transactions found.\n\n"
            "Start using the bot to see your transaction history!"
        )
        return

    history_text = "📜 Transaction History (Last 5)\n\n"

    for trans in transactions:
        emoji = format_transaction_type(trans["type"])
        amount_sign = "+" if trans["type"] in ["credit", "transfer_in", "redeem", "daily", "referral", "purchase"] else "-"
        timestamp = format_datetime(trans["timestamp"])

        history_text += (
            f"{emoji} {amount_sign}{trans['amount']:,} coins\n"
            f"📝 {trans['description']}\n"
            f"🕐 {timestamp}\n"
            f"{'-' * 30}\n"
        )

    await update.message.reply_text(history_text)
