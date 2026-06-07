"""
Admin command handlers for RepotechBot
Handles all admin-only commands
"""

from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import admin_only
from utils.helpers import validate_user_id, validate_amount, generate_key
from config import ADMIN_ID, BROADCAST_DELAY
import asyncio
import logging

logger = logging.getLogger(__name__)


@admin_only
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command - show admin menu"""
    admin_text = """
👑 Admin Commands Panel

📊 STATISTICS:
/stats - View bot statistics
/allusers - List all users with balances

👥 USER MANAGEMENT:
/userinfo <user_id> - Get user information
/ban <user_id> - Ban a user
/unban <user_id> - Unban a user
/resetuser <user_id> - Reset user balance to 0

💰 BALANCE MANAGEMENT:
/addbalance <user_id> <amount> - Add coins to user
/removebalance <user_id> <amount> - Remove coins from user

🎁 KEY MANAGEMENT:
/genkey <count> <coins> - Generate redeem keys
/listkeys - List all unused keys
/deletekey <key> - Delete a specific key

💳 PAYMENT MANAGEMENT:
/approve <user_id> <coins> - Approve coin purchase
/reject <user_id> <reason> - Reject coin purchase

📢 COMMUNICATION:
/broadcast <message> - Send message to all users

🏥 API MONITORING:
/apihealth - Check Free Fire API endpoints status
/sysinfo - Show system and deployment information

⚠️ Use these commands responsibly!
"""
    await update.message.reply_text(admin_text)


@admin_only
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command"""
    db = context.bot_data.get("db")

    total_users = await db.get_total_users()
    total_coins = await db.get_total_coins()
    total_transactions = await db.get_total_transactions()

    # Get additional stats
    leaderboard = await db.get_leaderboard(limit=1)
    richest_user = leaderboard[0] if leaderboard else None

    stats_text = f"""
📊 Bot Statistics

👥 Total Users: {total_users:,}
💰 Total Coins in Circulation: {total_coins:,}
📝 Total Transactions: {total_transactions:,}
"""

    if richest_user:
        stats_text += f"\n💎 Richest User: @{richest_user['username'] or richest_user['user_id']} ({richest_user['balance']:,} coins)"

    await update.message.reply_text(stats_text)


@admin_only
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /broadcast command"""
    db = context.bot_data.get("db")

    if not context.args:
        await update.message.reply_text(
            "❌ Usage: /broadcast <message>\n\n"
            "Example: /broadcast Hello everyone! New features added!"
        )
        return

    message = " ".join(context.args)
    user_ids = await db.get_user_ids()

    await update.message.reply_text(
        f"📢 Starting broadcast to {len(user_ids)} users...\n"
        f"This may take a while. Please wait."
    )

    success_count = 0
    failed_count = 0

    for user_id in user_ids:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📢 Broadcast Message:\n\n{message}"
            )
            success_count += 1
            await asyncio.sleep(BROADCAST_DELAY)  # Respect rate limits
        except Exception as e:
            failed_count += 1
            logger.error(f"Failed to send broadcast to {user_id}: {e}")

    await update.message.reply_text(
        f"✅ Broadcast completed!\n\n"
        f"✅ Sent: {success_count}\n"
        f"❌ Failed: {failed_count}\n"
        f"📊 Total: {len(user_ids)}"
    )

    logger.info(f"Broadcast completed: {success_count} sent, {failed_count} failed")


@admin_only
async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ban command"""
    db = context.bot_data.get("db")

    if not context.args:
        await update.message.reply_text(
            "❌ Usage: /ban <user_id>\n\n"
            "Example: /ban 123456789"
        )
        return

    user_id = validate_user_id(context.args[0])
    if not user_id:
        await update.message.reply_text("❌ Invalid user ID")
        return

    # Prevent banning admin
    if user_id == ADMIN_ID:
        await update.message.reply_text("❌ You cannot ban the admin!")
        return

    # Check if user exists
    user = await db.get_user(user_id)
    if not user:
        await update.message.reply_text("❌ User not found in database")
        return

    # Ban user
    await db.ban_user(user_id)
    await update.message.reply_text(
        f"✅ User {user_id} (@{user['username']}) has been banned"
    )

    # Notify user
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text="❌ You have been banned from using this bot.\n"
            "Contact the administrator if you believe this is a mistake."
        )
    except Exception as e:
        logger.error(f"Failed to notify banned user {user_id}: {e}")

    logger.info(f"Admin banned user {user_id}")


@admin_only
async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /unban command"""
    db = context.bot_data.get("db")

    if not context.args:
        await update.message.reply_text(
            "❌ Usage: /unban <user_id>\n\n"
            "Example: /unban 123456789"
        )
        return

    user_id = validate_user_id(context.args[0])
    if not user_id:
        await update.message.reply_text("❌ Invalid user ID")
        return

    # Check if user exists
    user = await db.get_user(user_id)
    if not user:
        await update.message.reply_text("❌ User not found in database")
        return

    # Unban user
    await db.unban_user(user_id)
    await update.message.reply_text(
        f"✅ User {user_id} (@{user['username']}) has been unbanned"
    )

    # Notify user
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text="✅ You have been unbanned! You can now use the bot again.\n"
            "Use /start to continue."
        )
    except Exception as e:
        logger.error(f"Failed to notify unbanned user {user_id}: {e}")

    logger.info(f"Admin unbanned user {user_id}")


@admin_only
async def addbalance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /addbalance command"""
    db = context.bot_data.get("db")

    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ Usage: /addbalance <user_id> <amount>\n\n"
            "Example: /addbalance 123456789 100"
        )
        return

    user_id = validate_user_id(context.args[0])
    amount = validate_amount(context.args[1])

    if not user_id or not amount:
        await update.message.reply_text("❌ Invalid user ID or amount")
        return

    # Check if user exists
    user = await db.get_user(user_id)
    if not user:
        await update.message.reply_text("❌ User not found in database")
        return

    # Add balance
    await db.update_balance(user_id, amount)
    await db.add_transaction(user_id, "credit", amount, "Admin added balance")

    # Get updated balance
    updated_user = await db.get_user(user_id)

    await update.message.reply_text(
        f"✅ Added {amount:,} coins to user {user_id}\n\n"
        f"👤 User: @{user['username']}\n"
        f"💰 Previous: {user['balance']:,} coins\n"
        f"💵 New: {updated_user['balance']:,} coins"
    )

    # Notify user
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"💰 Admin added {amount:,} coins to your account!\n"
            f"💵 New balance: {updated_user['balance']:,} coins"
        )
    except Exception as e:
        logger.error(f"Failed to notify user {user_id}: {e}")

    logger.info(f"Admin added {amount} coins to user {user_id}")


@admin_only
async def removebalance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /removebalance command"""
    db = context.bot_data.get("db")

    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ Usage: /removebalance <user_id> <amount>\n\n"
            "Example: /removebalance 123456789 50"
        )
        return

    user_id = validate_user_id(context.args[0])
    amount = validate_amount(context.args[1])

    if not user_id or not amount:
        await update.message.reply_text("❌ Invalid user ID or amount")
        return

    # Check if user exists
    user = await db.get_user(user_id)
    if not user:
        await update.message.reply_text("❌ User not found in database")
        return

    # Remove balance
    await db.update_balance(user_id, -amount)
    await db.add_transaction(user_id, "debit", amount, "Admin removed balance")

    # Get updated balance
    updated_user = await db.get_user(user_id)

    await update.message.reply_text(
        f"✅ Removed {amount:,} coins from user {user_id}\n\n"
        f"👤 User: @{user['username']}\n"
        f"💰 Previous: {user['balance']:,} coins\n"
        f"💵 New: {updated_user['balance']:,} coins"
    )

    # Notify user
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"⚠️ Admin removed {amount:,} coins from your account.\n"
            f"💵 New balance: {updated_user['balance']:,} coins"
        )
    except Exception as e:
        logger.error(f"Failed to notify user {user_id}: {e}")

    logger.info(f"Admin removed {amount} coins from user {user_id}")


@admin_only
async def allusers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /allusers command"""
    db = context.bot_data.get("db")

    users = await db.get_all_users()

    if not users:
        await update.message.reply_text("No users found in database")
        return

    users_text = "👥 All Users (sorted by balance)\n\n"

    for idx, user in enumerate(users[:50], 1):  # Limit to 50 users
        banned_emoji = "🚫" if user["is_banned"] else ""
        users_text += (
            f"{idx}. {banned_emoji} @{user['username'] or user['user_id']} "
            f"(ID: {user['user_id']})\n"
            f"   💰 {user['balance']:,} coins\n"
        )

    if len(users) > 50:
        users_text += f"\n... and {len(users) - 50} more users"

    await update.message.reply_text(users_text)


@admin_only
async def resetuser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /resetuser command"""
    db = context.bot_data.get("db")

    if not context.args:
        await update.message.reply_text(
            "❌ Usage: /resetuser <user_id>\n\n"
            "Example: /resetuser 123456789"
        )
        return

    user_id = validate_user_id(context.args[0])
    if not user_id:
        await update.message.reply_text("❌ Invalid user ID")
        return

    # Check if user exists
    user = await db.get_user(user_id)
    if not user:
        await update.message.reply_text("❌ User not found in database")
        return

    old_balance = user["balance"]

    # Reset balance
    await db.set_balance(user_id, 0)
    await db.add_transaction(user_id, "debit", old_balance, "Admin reset balance")

    await update.message.reply_text(
        f"✅ Reset balance for user {user_id}\n\n"
        f"👤 User: @{user['username']}\n"
        f"💰 Previous: {old_balance:,} coins\n"
        f"💵 New: 0 coins"
    )

    # Notify user
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"⚠️ Your balance has been reset by the admin.\n"
            f"💵 New balance: 0 coins"
        )
    except Exception as e:
        logger.error(f"Failed to notify user {user_id}: {e}")

    logger.info(f"Admin reset balance for user {user_id}")


@admin_only
async def genkey_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /genkey command"""
    db = context.bot_data.get("db")
    admin_id = update.effective_user.id

    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ Usage: /genkey <count> <coins>\n\n"
            "Example: /genkey 5 100\n"
            "(Generate 5 keys worth 100 coins each)"
        )
        return

    count = validate_amount(context.args[0])
    coins = validate_amount(context.args[1])

    if not count or not coins:
        await update.message.reply_text("❌ Invalid count or coins amount")
        return

    if count > 50:
        await update.message.reply_text("❌ Maximum 50 keys per generation")
        return

    # Generate keys
    keys_generated = []
    for _ in range(count):
        key = generate_key()
        await db.create_key(key, coins, admin_id)
        keys_generated.append(key)

    keys_text = f"✅ Generated {count} keys worth {coins} coins each:\n\n"
    for idx, key in enumerate(keys_generated, 1):
        keys_text += f"{idx}. `{key}`\n"

    keys_text += f"\n💡 Users can redeem with /redeem <key>"

    await update.message.reply_text(keys_text, parse_mode="Markdown")

    logger.info(f"Admin generated {count} keys worth {coins} coins each")


@admin_only
async def listkeys_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /listkeys command"""
    db = context.bot_data.get("db")

    keys = await db.get_unused_keys()

    if not keys:
        await update.message.reply_text("No unused keys found")
        return

    keys_text = "🎁 Unused Redeem Keys\n\n"

    for idx, key in enumerate(keys[:30], 1):  # Limit to 30 keys
        keys_text += f"{idx}. `{key['key']}` - {key['coins']} coins\n"

    if len(keys) > 30:
        keys_text += f"\n... and {len(keys) - 30} more keys"

    await update.message.reply_text(keys_text, parse_mode="Markdown")


@admin_only
async def deletekey_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /deletekey command"""
    db = context.bot_data.get("db")

    if not context.args:
        await update.message.reply_text(
            "❌ Usage: /deletekey <key>\n\n"
            "Example: /deletekey abc123def456"
        )
        return

    key = context.args[0]

    # Check if key exists
    key_data = await db.get_key(key)
    if not key_data:
        await update.message.reply_text("❌ Key not found")
        return

    # Delete key
    await db.delete_key(key)

    await update.message.reply_text(
        f"✅ Key deleted successfully\n\n"
        f"🎁 Key: `{key}`\n"
        f"💰 Worth: {key_data['coins']} coins",
        parse_mode="Markdown"
    )

    logger.info(f"Admin deleted key {key}")


@admin_only
async def approve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /approve command"""
    db = context.bot_data.get("db")

    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ Usage: /approve <user_id> <coins>\n\n"
            "Example: /approve 123456789 100"
        )
        return

    user_id = validate_user_id(context.args[0])
    coins = validate_amount(context.args[1])

    if not user_id or not coins:
        await update.message.reply_text("❌ Invalid user ID or coins amount")
        return

    # Check if user exists
    user = await db.get_user(user_id)
    if not user:
        await update.message.reply_text("❌ User not found in database")
        return

    # Add coins
    await db.update_balance(user_id, coins)
    await db.add_transaction(user_id, "purchase", coins, f"Coin purchase approved - {coins} coins")

    # Get updated balance
    updated_user = await db.get_user(user_id)

    await update.message.reply_text(
        f"✅ Approved coin purchase for user {user_id}\n\n"
        f"👤 User: @{user['username']}\n"
        f"💰 Coins added: {coins:,}\n"
        f"💵 New balance: {updated_user['balance']:,} coins"
    )

    # Notify user
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"✅ Your coin purchase has been approved!\n\n"
            f"💰 Coins added: {coins:,}\n"
            f"💵 New balance: {updated_user['balance']:,} coins\n\n"
            f"Thank you for your purchase!"
        )
    except Exception as e:
        logger.error(f"Failed to notify user {user_id}: {e}")

    logger.info(f"Admin approved {coins} coins for user {user_id}")


@admin_only
async def reject_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /reject command"""
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ Usage: /reject <user_id> <reason>\n\n"
            "Example: /reject 123456789 Invalid payment proof"
        )
        return

    user_id = validate_user_id(context.args[0])
    reason = " ".join(context.args[1:])

    if not user_id:
        await update.message.reply_text("❌ Invalid user ID")
        return

    await update.message.reply_text(
        f"✅ Rejected coin purchase for user {user_id}\n"
        f"📝 Reason: {reason}"
    )

    # Notify user
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"❌ Your coin purchase has been rejected.\n\n"
            f"📝 Reason: {reason}\n\n"
            f"Please contact support if you have questions."
        )
    except Exception as e:
        logger.error(f"Failed to notify user {user_id}: {e}")

    logger.info(f"Admin rejected purchase for user {user_id}: {reason}")


@admin_only
async def userinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /userinfo command"""
    db = context.bot_data.get("db")

    if not context.args:
        await update.message.reply_text(
            "❌ Usage: /userinfo <user_id>\n\n"
            "Example: /userinfo 123456789"
        )
        return

    user_id = validate_user_id(context.args[0])
    if not user_id:
        await update.message.reply_text("❌ Invalid user ID")
        return

    # Get user info
    user = await db.get_user(user_id)
    if not user:
        await update.message.reply_text("❌ User not found in database")
        return

    # Get referral count
    referral_count = await db.get_referral_count(user_id)

    info_text = f"""
👤 User Information

🆔 User ID: {user['user_id']}
👤 Username: @{user['username'] or 'N/A'}
💰 Balance: {user['balance']:,} coins
🚫 Banned: {'Yes' if user['is_banned'] else 'No'}
👥 Referrals: {referral_count}
📅 Joined: {user['created_at'][:10]}
🎁 Last Daily: {user['last_daily'][:10] if user['last_daily'] else 'Never'}
"""

    if user['referred_by']:
        referrer = await db.get_user(user['referred_by'])
        if referrer:
            info_text += f"🔗 Referred by: @{referrer['username']} ({user['referred_by']})\n"

    await update.message.reply_text(info_text)


@admin_only
async def sysinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /sysinfo command - Show system and deployment information"""
    import platform
    import sys
    import os
    from datetime import datetime

    # Get system information
    python_version = sys.version.split()[0]
    platform_info = platform.platform()

    # Check if auth server code is present
    auth_server_exists = os.path.exists("auth_server.py")
    run_both_exists = os.path.exists("run_both.py")

    # Try to detect if we're using localhost auth
    get_jwt_path = "freefire/get_jwt.py"
    using_localhost = False
    if os.path.exists(get_jwt_path):
        with open(get_jwt_path, 'r') as f:
            content = f.read()
            using_localhost = "localhost:8001" in content

    # Get current git commit (if available)
    git_commit = "Unknown"
    try:
        import subprocess
        result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'],
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            git_commit = result.stdout.strip()
    except:
        pass

    info_text = f"""
🖥️ System Information

📊 Platform: {platform_info}
🐍 Python: {python_version}
🔖 Git Commit: {git_commit}
⏰ Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 Auth Server Status:
• auth_server.py: {'✅ Present' if auth_server_exists else '❌ Missing'}
• run_both.py: {'✅ Present' if run_both_exists else '❌ Missing'}
• Using localhost:8001: {'✅ YES' if using_localhost else '❌ NO (using ggblueshark)'}

💡 If "Using localhost:8001" shows NO, Railway is running old code.
   Wait 3-5 minutes after git push for deployment to complete.

📝 Test deployment with /likes command.
"""

    await update.message.reply_text(info_text)
