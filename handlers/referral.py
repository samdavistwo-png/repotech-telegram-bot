"""
Referral command handlers for RepotechBot
Handles /referral, /referrals, and /topref commands
"""

from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import check_banned, user_exists
import logging

logger = logging.getLogger(__name__)


@check_banned
@user_exists
async def referral_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /referral command"""
    user_id = update.effective_user.id
    bot_username = context.bot.username

    referral_link = f"https://t.me/{bot_username}?start={user_id}"

    await update.message.reply_text(
        f"👥 Your Referral Link\n\n"
        f"🔗 Share this link with your friends:\n"
        f"`{referral_link}`\n\n"
        f"💰 Rewards:\n"
        f"• You get 50 coins for each friend who joins\n"
        f"• Your friend gets 50 coins as a welcome bonus\n\n"
        f"📊 Use /referrals to see how many people you've referred\n"
        f"🏆 Use /topref to see the top referrers",
        parse_mode="Markdown"
    )


@check_banned
@user_exists
async def referrals_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /referrals command"""
    db = context.bot_data.get("db")
    user_id = update.effective_user.id

    referral_count = await db.get_referral_count(user_id)

    total_earnings = referral_count * 50  # 50 coins per referral

    await update.message.reply_text(
        f"👥 Your Referral Stats\n\n"
        f"📊 Total Referrals: {referral_count}\n"
        f"💰 Total Earned: {total_earnings:,} coins\n\n"
        f"💡 Keep sharing your referral link to earn more coins!\n"
        f"Use /referral to get your link"
    )


@check_banned
@user_exists
async def topref_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /topref command"""
    db = context.bot_data.get("db")

    top_referrers = await db.get_top_referrers(limit=10)

    if not top_referrers:
        await update.message.reply_text(
            "🏆 Top Referrers\n\n"
            "No referrals yet. Be the first to refer friends and earn coins!"
        )
        return

    leaderboard_text = "🏆 Top 10 Referrers\n\n"

    medals = {1: "🥇", 2: "🥈", 3: "🥉"}

    for idx, referrer in enumerate(top_referrers, 1):
        medal = medals.get(idx, f"{idx}.")
        username = referrer['username'] or f"User {referrer['user_id']}"
        count = referrer['referral_count']
        earnings = count * 50

        leaderboard_text += (
            f"{medal} @{username}\n"
            f"   👥 {count} referrals | 💰 {earnings:,} coins earned\n\n"
        )

    leaderboard_text += "💡 Use /referral to get your referral link!"

    await update.message.reply_text(leaderboard_text)
