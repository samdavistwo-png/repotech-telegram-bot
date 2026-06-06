"""
Decorators for RepotechBot
Provides admin check and banned user check decorators
"""

from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID
import logging

logger = logging.getLogger(__name__)


def admin_only(func):
    """Decorator to restrict command to admin only"""

    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id

        if user_id != ADMIN_ID:
            await update.message.reply_text(
                "Access Denied. This command is only available to administrators."
            )
            logger.warning(f"Unauthorized admin access attempt by user {user_id}")
            return

        return await func(update, context, *args, **kwargs)

    return wrapper


def check_banned(func):
    """Decorator to check if user is banned"""

    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        db = context.bot_data.get("db")
        user_id = update.effective_user.id

        # Get user from database
        user = await db.get_user(user_id)

        # Check if user is banned
        if user and user["is_banned"]:
            await update.message.reply_text(
                "You have been banned from using this bot. Contact the administrator if you believe this is a mistake."
            )
            logger.info(f"Banned user {user_id} attempted to use command")
            return

        return await func(update, context, *args, **kwargs)

    return wrapper


def user_exists(func):
    """Decorator to ensure user exists in database"""

    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        db = context.bot_data.get("db")
        user_id = update.effective_user.id
        username = update.effective_user.username

        # Get or create user
        user = await db.get_user(user_id)
        if not user:
            # Create user without referral
            await db.create_user(user_id, username)
            logger.info(f"Auto-created user {user_id} in database")

        return await func(update, context, *args, **kwargs)

    return wrapper
