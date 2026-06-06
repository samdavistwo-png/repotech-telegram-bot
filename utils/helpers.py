"""
Helper utilities for RepotechBot
Provides common utility functions
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional


def generate_key(length: int = 16) -> str:
    """Generate a random hexadecimal key"""
    return secrets.token_hex(length // 2)


def format_datetime(dt_string: str) -> str:
    """Format datetime string for display"""
    try:
        dt = datetime.fromisoformat(dt_string)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return dt_string


def can_claim_daily(last_daily: Optional[str]) -> bool:
    """Check if user can claim daily reward"""
    if not last_daily:
        return True

    try:
        last_claim = datetime.fromisoformat(last_daily)
        now = datetime.now()
        time_diff = now - last_claim

        # Can claim if more than 24 hours have passed
        return time_diff >= timedelta(hours=24)
    except:
        return True


def time_until_next_daily(last_daily: str) -> str:
    """Calculate time remaining until next daily claim"""
    try:
        last_claim = datetime.fromisoformat(last_daily)
        next_claim = last_claim + timedelta(hours=24)
        now = datetime.now()

        if now >= next_claim:
            return "Available now"

        time_diff = next_claim - now
        hours = int(time_diff.total_seconds() // 3600)
        minutes = int((time_diff.total_seconds() % 3600) // 60)

        return f"{hours}h {minutes}m"
    except:
        return "Available now"


def format_transaction_type(trans_type: str) -> str:
    """Format transaction type for display"""
    emoji_map = {
        "credit": "➕",
        "debit": "➖",
        "transfer_in": "📥",
        "transfer_out": "📤",
        "redeem": "🎁",
        "daily": "📅",
        "referral": "👥",
        "purchase": "💰",
    }
    return emoji_map.get(trans_type, "💵")


def validate_user_id(user_id_str: str) -> Optional[int]:
    """Validate and convert user ID string to integer"""
    try:
        user_id = int(user_id_str)
        if user_id > 0:
            return user_id
        return None
    except (ValueError, TypeError):
        return None


def validate_amount(amount_str: str) -> Optional[int]:
    """Validate and convert amount string to integer"""
    try:
        amount = int(amount_str)
        if amount > 0:
            return amount
        return None
    except (ValueError, TypeError):
        return None


def format_balance(balance: int) -> str:
    """Format balance with emoji"""
    return f"💰 {balance:,} coins"


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
