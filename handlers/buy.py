"""
Buy coins command handlers for RepotechBot
Handles /buy and /paid commands
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from utils.decorators import check_banned, user_exists
from config import BUY_PACKAGES, UPI_ID, ADMIN_ID
import logging

logger = logging.getLogger(__name__)


@check_banned
@user_exists
async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /buy command"""
    # Create inline keyboard with packages
    keyboard = [
        [
            InlineKeyboardButton(
                "50 Coins - Rs.30",
                callback_data="buy_50_coins"
            )
        ],
        [
            InlineKeyboardButton(
                "100 Coins - Rs.50",
                callback_data="buy_100_coins"
            )
        ],
        [
            InlineKeyboardButton(
                "200 Coins - Rs.90",
                callback_data="buy_200_coins"
            )
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "💳 Buy Coin Packages\n\n"
        "Select a package to purchase:\n\n"
        "💰 50 Coins = Rs.30\n"
        "💰 100 Coins = Rs.50\n"
        "💰 200 Coins = Rs.90\n\n"
        "Click a button below to see payment details:",
        reply_markup=reply_markup
    )


async def buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle buy package callback"""
    query = update.callback_query
    await query.answer()

    package = query.data.replace("buy_", "")

    if package not in BUY_PACKAGES:
        await query.edit_message_text("❌ Invalid package selected")
        return

    package_info = BUY_PACKAGES[package]
    coins = package_info["coins"]
    price = package_info["price"]

    payment_text = f"""
💳 Payment Details

📦 Package: {coins} Coins
💵 Amount: Rs.{price}

💳 Payment Method: UPI
🆔 UPI ID: `{UPI_ID}`

📝 Instructions:
1. Send Rs.{price} to the UPI ID above
2. Copy your transaction ID
3. Use command: /paid {package} <transaction_id>

Example:
/paid {package} UTR123456789

⚠️ Important:
• Do not share fake transaction IDs
• Admin will verify and approve manually
• Coins will be added after approval
"""

    await query.edit_message_text(payment_text, parse_mode="Markdown")


@check_banned
@user_exists
async def paid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /paid command"""
    db = context.bot_data.get("db")
    user_id = update.effective_user.id
    username = update.effective_user.username

    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ Usage: /paid <package> <transaction_id>\n\n"
            "Example: /paid 50_coins UTR123456789\n\n"
            "Available packages:\n"
            "• 50_coins (Rs.30)\n"
            "• 100_coins (Rs.50)\n"
            "• 200_coins (Rs.90)"
        )
        return

    package = context.args[0]
    transaction_id = context.args[1]

    if package not in BUY_PACKAGES:
        await update.message.reply_text(
            "❌ Invalid package!\n\n"
            "Available packages:\n"
            "• 50_coins\n"
            "• 100_coins\n"
            "• 200_coins"
        )
        return

    package_info = BUY_PACKAGES[package]
    coins = package_info["coins"]
    price = package_info["price"]

    # Save payment record
    await db.add_payment(user_id, package, transaction_id, price)

    # Notify user
    await update.message.reply_text(
        f"✅ Payment Submitted!\n\n"
        f"📦 Package: {coins} Coins\n"
        f"💵 Amount: Rs.{price}\n"
        f"🆔 Transaction ID: {transaction_id}\n\n"
        f"⏳ Your payment is being verified by the admin.\n"
        f"You will be notified once approved.\n\n"
        f"Thank you for your patience!"
    )

    # Notify admin
    try:
        admin_notification = f"""
🔔 New Payment Submission!

👤 User: @{username or user_id}
🆔 User ID: {user_id}
📦 Package: {coins} Coins
💵 Amount: Rs.{price}
🆔 Transaction ID: {transaction_id}

To approve: /approve {user_id} {coins}
To reject: /reject {user_id} <reason>
"""
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_notification
        )
    except Exception as e:
        logger.error(f"Failed to notify admin about payment: {e}")

    logger.info(f"User {user_id} submitted payment for {package}: {transaction_id}")
