"""
Free Fire Likes - Manual Processing System
Users submit requests, admin processes manually
"""

from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import check_banned, user_exists
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Constants
LIKES_COST = 50
LIKES_TO_SEND = 100
DAILY_LIMIT = 3


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
    """Handle /likes command - Manual processing by admin"""
    db = context.bot_data.get("db")
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    try:
        # Validate input
        if not context.args or len(context.args) < 1:
            await update.message.reply_text(
                "❌ Please provide a Free Fire UID!\n\n"
                "📝 Usage: /likes <uid>\n"
                "Example: /likes 1234567890\n\n"
                f"💰 Cost: {LIKES_COST} coins\n"
                f"❤️ Likes sent: {LIKES_TO_SEND}\n"
                f"📅 Daily limit: {DAILY_LIMIT} requests\n\n"
                "⏱️ Processing time: 5-30 minutes\n"
                "📬 You'll be notified when complete"
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

        # Deduct coins immediately
        new_balance = user['balance'] - LIKES_COST
        await db.update_balance(user_id, -LIKES_COST)
        await db.add_transaction(
            user_id, "likes", -LIKES_COST,
            f"Likes request for {target_uid} (pending)"
        )
        await db.add_likes_usage(user_id, target_uid, 0, LIKES_COST)

        # Send to admin for manual processing
        admin_message = (
            f"🔔 NEW LIKES REQUEST\n\n"
            f"👤 User: @{username} (ID: {user_id})\n"
            f"🎯 Free Fire UID: {target_uid}\n"
            f"❤️ Likes: {LIKES_TO_SEND}\n"
            f"💰 Paid: {LIKES_COST} coins\n\n"
            f"📝 Instructions:\n"
            f"1. Process this request manually\n"
            f"2. Send {LIKES_TO_SEND} likes to UID: {target_uid}\n"
            f"3. Reply to user when done:\n"
            f"   /msg {user_id} Your {LIKES_TO_SEND} likes have been sent to {target_uid}! ✅"
        )

        # Get admin IDs from environment or use default
        admin_ids = [7024084218]  # Your admin ID
        for admin_id in admin_ids:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=admin_message
                )
            except:
                pass

        # Confirm to user
        requests_left = DAILY_LIMIT - (today_requests + 1)

        await update.message.reply_text(
            f"✅ Request Submitted!\n\n"
            f"🎯 Free Fire UID: {target_uid}\n"
            f"❤️ Likes: {LIKES_TO_SEND}\n"
            f"💰 Deducted: {LIKES_COST} coins\n"
            f"💳 New Balance: {new_balance} coins\n\n"
            f"⏱️ Processing Time: 5-30 minutes\n"
            f"📬 You'll be notified when complete\n\n"
            f"📅 Requests left today: {requests_left}/{DAILY_LIMIT}\n\n"
            f"⚡ Your request is being processed by admin..."
        )

        logger.info(f"Manual likes request: User {user_id} -> UID {target_uid}")

    except Exception as e:
        logger.error(f"❌ ERROR in likes command: {e}", exc_info=True)
        try:
            await update.message.reply_text(
                f"❌ System Error!\n\n"
                f"Details: {str(e)[:100]}\n\n"
                "Please contact admin."
            )
        except:
            pass


async def likestatus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check status of likes request"""
    await update.message.reply_text(
        "📊 Likes Request Status\n\n"
        "All likes requests are processed manually by admin.\n"
        "Typical processing time: 5-30 minutes\n\n"
        "You will receive a message when your request is complete.\n\n"
        "If you haven't received confirmation after 1 hour, please contact admin."
    )


async def likehistory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show likes history"""
    db = context.bot_data.get("db")
    user_id = update.effective_user.id

    try:
        # Get recent likes requests
        history = await db.get_likes_history(user_id, limit=10)

        if not history:
            await update.message.reply_text(
                "📊 Likes History\n\n"
                "No likes requests yet.\n\n"
                "Use /likes <uid> to send likes!"
            )
            return

        msg = "📊 Your Likes History\n\n"
        for i, record in enumerate(history, 1):
            uid = record.get('target_uid', 'Unknown')
            likes = record.get('likes_sent', LIKES_TO_SEND)
            date = record.get('created_at', '')[:10]
            msg += f"{i}. UID: {uid} | Likes: {likes} | Date: {date}\n"

        await update.message.reply_text(msg)

    except Exception as e:
        logger.error(f"Error in likehistory: {e}")
        await update.message.reply_text("❌ Error fetching history")
