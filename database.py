"""
Database module for RepotechBot
Handles SQLite database operations with async support
"""

import aiosqlite
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from config import DATABASE_PATH, INITIAL_BALANCE

logger = logging.getLogger(__name__)


class Database:
    """Database handler for RepotechBot"""

    def __init__(self, db_path: str = DATABASE_PATH):
        """Initialize database connection"""
        self.db_path = db_path

    async def init_db(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Users table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    balance INTEGER DEFAULT 0,
                    is_banned INTEGER DEFAULT 0,
                    referred_by INTEGER,
                    created_at TEXT,
                    last_daily TEXT
                )
            """)

            # Transactions table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    type TEXT,
                    amount INTEGER,
                    description TEXT,
                    timestamp TEXT
                )
            """)

            # Referrals table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS referrals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referrer_id INTEGER,
                    referred_id INTEGER,
                    timestamp TEXT
                )
            """)

            # Keys table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS keys (
                    key TEXT PRIMARY KEY,
                    coins INTEGER,
                    created_by INTEGER,
                    is_used INTEGER DEFAULT 0,
                    used_by INTEGER,
                    created_at TEXT,
                    used_at TEXT
                )
            """)

            # Likes usage table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS likes_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    uid TEXT,
                    likes_sent INTEGER,
                    coins_spent INTEGER,
                    timestamp TEXT
                )
            """)

            # Payments table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    package TEXT,
                    transaction_id TEXT,
                    amount INTEGER,
                    status TEXT,
                    timestamp TEXT
                )
            """)

            await db.commit()
            logger.info("Database initialized successfully")

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by user_id"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def create_user(
        self, user_id: int, username: str = None, referred_by: int = None
    ) -> bool:
        """Create new user"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    """INSERT INTO users (user_id, username, balance, created_at, referred_by)
                       VALUES (?, ?, ?, ?, ?)""",
                    (user_id, username, INITIAL_BALANCE, datetime.now().isoformat(), referred_by),
                )
                await db.commit()

                # Add transaction for initial balance
                await self.add_transaction(
                    user_id, "credit", INITIAL_BALANCE, "Initial balance"
                )

                logger.info(f"Created new user: {user_id}")
                return True
            except Exception as e:
                logger.error(f"Error creating user {user_id}: {e}")
                return False

    async def update_balance(self, user_id: int, amount: int) -> bool:
        """Update user balance"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                    (amount, user_id),
                )
                await db.commit()
                return True
            except Exception as e:
                logger.error(f"Error updating balance for {user_id}: {e}")
                return False

    async def set_balance(self, user_id: int, balance: int) -> bool:
        """Set user balance to specific amount"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    "UPDATE users SET balance = ? WHERE user_id = ?",
                    (balance, user_id),
                )
                await db.commit()
                return True
            except Exception as e:
                logger.error(f"Error setting balance for {user_id}: {e}")
                return False

    async def ban_user(self, user_id: int) -> bool:
        """Ban a user"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    "UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,)
                )
                await db.commit()
                return True
            except Exception as e:
                logger.error(f"Error banning user {user_id}: {e}")
                return False

    async def unban_user(self, user_id: int) -> bool:
        """Unban a user"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    "UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,)
                )
                await db.commit()
                return True
            except Exception as e:
                logger.error(f"Error unbanning user {user_id}: {e}")
                return False

    async def add_transaction(
        self, user_id: int, trans_type: str, amount: int, description: str
    ) -> bool:
        """Add transaction record"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    """INSERT INTO transactions (user_id, type, amount, description, timestamp)
                       VALUES (?, ?, ?, ?, ?)""",
                    (user_id, trans_type, amount, description, datetime.now().isoformat()),
                )
                await db.commit()
                return True
            except Exception as e:
                logger.error(f"Error adding transaction: {e}")
                return False

    async def get_transaction_history(
        self, user_id: int, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get user transaction history"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """SELECT * FROM transactions WHERE user_id = ?
                   ORDER BY timestamp DESC LIMIT ?""",
                (user_id, limit),
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def add_referral(self, referrer_id: int, referred_id: int) -> bool:
        """Add referral record"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    """INSERT INTO referrals (referrer_id, referred_id, timestamp)
                       VALUES (?, ?, ?)""",
                    (referrer_id, referred_id, datetime.now().isoformat()),
                )
                await db.commit()
                return True
            except Exception as e:
                logger.error(f"Error adding referral: {e}")
                return False

    async def get_referral_count(self, user_id: int) -> int:
        """Get number of referrals for a user"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,)
            )
            count = await cursor.fetchone()
            return count[0] if count else 0

    async def get_top_referrers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top referrers"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """SELECT u.user_id, u.username, COUNT(r.referred_id) as referral_count
                   FROM users u
                   LEFT JOIN referrals r ON u.user_id = r.referrer_id
                   GROUP BY u.user_id
                   HAVING referral_count > 0
                   ORDER BY referral_count DESC
                   LIMIT ?""",
                (limit,),
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def create_key(self, key: str, coins: int, created_by: int) -> bool:
        """Create a redeem key"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    """INSERT INTO keys (key, coins, created_by, created_at)
                       VALUES (?, ?, ?, ?)""",
                    (key, coins, created_by, datetime.now().isoformat()),
                )
                await db.commit()
                return True
            except Exception as e:
                logger.error(f"Error creating key: {e}")
                return False

    async def get_key(self, key: str) -> Optional[Dict[str, Any]]:
        """Get key information"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM keys WHERE key = ?", (key,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def redeem_key(self, key: str, user_id: int) -> bool:
        """Mark key as redeemed"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    """UPDATE keys SET is_used = 1, used_by = ?, used_at = ?
                       WHERE key = ?""",
                    (user_id, datetime.now().isoformat(), key),
                )
                await db.commit()
                return True
            except Exception as e:
                logger.error(f"Error redeeming key: {e}")
                return False

    async def get_unused_keys(self) -> List[Dict[str, Any]]:
        """Get all unused keys"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM keys WHERE is_used = 0 ORDER BY created_at DESC"
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def delete_key(self, key: str) -> bool:
        """Delete a key"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute("DELETE FROM keys WHERE key = ?", (key,))
                await db.commit()
                return True
            except Exception as e:
                logger.error(f"Error deleting key: {e}")
                return False

    async def count_redeems_today(self, user_id: int) -> int:
        """Count how many keys user redeemed today"""
        async with aiosqlite.connect(self.db_path) as db:
            today = datetime.now().date().isoformat()
            cursor = await db.execute(
                """SELECT COUNT(*) FROM keys
                   WHERE used_by = ? AND DATE(used_at) = ?""",
                (user_id, today),
            )
            count = await cursor.fetchone()
            return count[0] if count else 0

    async def update_last_daily(self, user_id: int) -> bool:
        """Update last daily claim timestamp"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    "UPDATE users SET last_daily = ? WHERE user_id = ?",
                    (datetime.now().isoformat(), user_id),
                )
                await db.commit()
                return True
            except Exception as e:
                logger.error(f"Error updating last_daily: {e}")
                return False

    async def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top users by balance"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """SELECT user_id, username, balance
                   FROM users
                   ORDER BY balance DESC
                   LIMIT ?""",
                (limit,),
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT user_id, username, balance, is_banned FROM users ORDER BY balance DESC"
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_total_users(self) -> int:
        """Get total number of users"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM users")
            count = await cursor.fetchone()
            return count[0] if count else 0

    async def get_total_coins(self) -> int:
        """Get total coins in circulation"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT SUM(balance) FROM users")
            total = await cursor.fetchone()
            return total[0] if total and total[0] else 0

    async def get_total_transactions(self) -> int:
        """Get total number of transactions"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM transactions")
            count = await cursor.fetchone()
            return count[0] if count else 0

    async def add_payment(
        self, user_id: int, package: str, transaction_id: str, amount: int
    ) -> bool:
        """Add payment record"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    """INSERT INTO payments (user_id, package, transaction_id, amount, status, timestamp)
                       VALUES (?, ?, ?, ?, 'pending', ?)""",
                    (user_id, package, transaction_id, amount, datetime.now().isoformat()),
                )
                await db.commit()
                return True
            except Exception as e:
                logger.error(f"Error adding payment: {e}")
                return False

    async def update_payment_status(
        self, user_id: int, transaction_id: str, status: str
    ) -> bool:
        """Update payment status"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    """UPDATE payments SET status = ?
                       WHERE user_id = ? AND transaction_id = ?""",
                    (status, user_id, transaction_id),
                )
                await db.commit()
                return True
            except Exception as e:
                logger.error(f"Error updating payment status: {e}")
                return False

    async def get_pending_payments(self) -> List[Dict[str, Any]]:
        """Get all pending payments"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """SELECT * FROM payments
                   WHERE status = 'pending'
                   ORDER BY timestamp DESC"""
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_user_ids(self) -> List[int]:
        """Get all user IDs for broadcasting"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT user_id FROM users WHERE is_banned = 0")
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

    async def count_likes_today(self, user_id: int, today_start: str) -> int:
        """Count likes requests user made today"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT COUNT(*) FROM likes_usage WHERE user_id = ? AND timestamp >= ?",
                (user_id, today_start)
            )
            row = await cursor.fetchone()
            return row[0] if row else 0

    async def add_likes_usage(
        self, user_id: int, uid: str, likes_sent: int, coins_spent: int
    ) -> bool:
        """Add likes usage record"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    """INSERT INTO likes_usage (user_id, uid, likes_sent, coins_spent, timestamp)
                       VALUES (?, ?, ?, ?, ?)""",
                    (user_id, uid, likes_sent, coins_spent, datetime.now().isoformat()),
                )
                await db.commit()
                return True
            except Exception as e:
                logger.error(f"Error adding likes usage: {e}")
                return False

    async def get_likes_history(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get user's likes history"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """SELECT uid, likes_sent, coins_spent, timestamp
                   FROM likes_usage
                   WHERE user_id = ?
                   ORDER BY timestamp DESC
                   LIMIT ?""",
                (user_id, limit)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
