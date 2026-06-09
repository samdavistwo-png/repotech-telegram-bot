"""
Disabled Free Fire Likes Handlers
After Garena's OB51 patch, likes service is no longer operational
"""

from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import check_banned
import logging

logger = logging.getLogger(__name__)


@check_banned
async def likes_disabled_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /likes command - Service disabled after OB51 patch"""

    message = """
⚠️ **Free Fire Likes Service - Temporarily Unavailable**

🫂 Hey survivor! After the **OB51 update**, Garena has made major changes to the Like system.

🔥 **What Changed:**
• Level 2 accounts can no longer send likes ❌
• Level 9 accounts: Limited to ~20 likes
• Level 15 accounts: Limited to ~200 likes
• Only Level 40+ accounts appear to work without limits

💔 **Impact on Our Service:**
Our free like service relied on automated Level 2 guest accounts, which are now completely blocked from sending likes.

📢 **Current Status:**
The free like service is **closed until further updates** while we explore alternatives.

💰 **Good News:**
All other bot features work perfectly:
✅ Coin system
✅ Referral rewards (50 coins per friend!)
✅ Daily rewards (10-50 coins every 24h)
✅ Transfer coins to friends
✅ Leaderboard competition
✅ Buy coins packages

🗒 **Thank You:**
We appreciate your understanding! We're now **7K+ members strong**! 🥈

Use /help to see all available features! 💎
"""

    await update.message.reply_text(message, parse_mode='Markdown')
    logger.info(f"User {update.effective_user.id} tried to use disabled likes service")


@check_banned
async def likestatus_disabled_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /likestatus command - Service disabled"""

    message = """
📊 **Likes Service Status**

🔴 **Status:** Service Closed

After Garena's OB51 patch update, the free likes service is no longer operational due to platform restrictions on Level 2 accounts.

Use /likes for more information about the closure.

💰 Meanwhile, enjoy our other features:
• /daily - Claim your daily reward
• /referral - Earn coins by inviting friends
• /leaderboard - Compete for top spot!
"""

    await update.message.reply_text(message)


@check_banned
async def likehistory_disabled_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /likehistory command - Service disabled"""

    message = """
📜 **Likes History**

The Free Fire likes service is currently closed due to Garena's OB51 patch changes.

Your previous likes history (if any) has been preserved in our database, but the service is not accepting new requests at this time.

Use /likes for more information about why the service is closed.

🎁 **Try these instead:**
• /history - View your coin transaction history
• /referrals - See who you've referred
• /balance - Check your current coins
"""

    await update.message.reply_text(message)
