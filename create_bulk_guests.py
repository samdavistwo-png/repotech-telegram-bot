"""
Bulk Guest Account Creator
Creates 100 new Free Fire guest accounts using multiple methods
"""

import asyncio
import json
import time
import logging
from pathlib import Path
import sys

# Add freefire directory to path
sys.path.insert(0, str(Path(__file__).parent / 'freefire'))

from temp_account_creator import create_multiple_guest_accounts
from ffmax_bulk_creator import create_bulk_accounts
from working_bulk_system import create_working_guest_account

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SAVE_FILE = Path(__file__).parent / "freefire" / "guests_manager" / "new_guests_2026.json"
BACKUP_FILE = Path(__file__).parent / "freefire" / "guests_manager" / "guests_converted.backup.json"
MAIN_FILE = Path(__file__).parent / "freefire" / "guests_manager" / "guests_converted.json"


async def method1_temp_accounts(count: int) -> list:
    """Create accounts using temp_account_creator (fast, async)"""
    logger.info(f"Method 1: Creating {count} accounts via temp_account_creator...")
    try:
        accounts = await create_multiple_guest_accounts(count)
        logger.info(f"Method 1: Created {len(accounts)} accounts")
        return accounts
    except Exception as e:
        logger.error(f"Method 1 failed: {e}")
        return []


def method2_ffmax_accounts(count: int) -> list:
    """Create FFMax accounts (sync, with delay)"""
    logger.info(f"Method 2: Creating {count} accounts via ffmax_bulk_creator...")
    try:
        # Use regular FF (not FFMax) for broader compatibility
        accounts = create_bulk_accounts(count=count, delay=3.0, use_ffmax=False)
        logger.info(f"Method 2: Created {len(accounts)} accounts")
        return accounts if accounts else []
    except Exception as e:
        logger.error(f"Method 2 failed: {e}")
        return []


def method3_signed_accounts(count: int) -> list:
    """Create accounts using signed API method"""
    logger.info(f"Method 3: Creating {count} accounts via working_bulk_system...")
    accounts = []
    for i in range(1, count + 1):
        try:
            account = create_working_guest_account(i)
            if account.get('success'):
                accounts.append({
                    'uid': str(account['uid']),
                    'password': account['password']
                })
                logger.info(f"Method 3: Created account {i}/{count} - UID: {account['uid']}")
            else:
                logger.warning(f"Method 3: Account {i}/{count} failed: {account.get('error', 'Unknown error')}")
            time.sleep(3)  # Rate limiting
        except Exception as e:
            logger.error(f"Method 3 account {i} failed: {e}")
            continue

    logger.info(f"Method 3: Created {len(accounts)} accounts")
    return accounts


async def create_100_accounts():
    """Create 100 accounts using multiple methods for redundancy"""
    all_accounts = []

    # Method 1: 50 accounts (fast async method)
    logger.info("=" * 70)
    logger.info("STARTING METHOD 1: Temp Account Creator (50 accounts)")
    logger.info("=" * 70)
    batch1 = await method1_temp_accounts(50)
    all_accounts.extend(batch1)
    logger.info(f"✅ Total so far: {len(all_accounts)} accounts")

    await asyncio.sleep(10)  # Pause between methods

    # Method 2: 30 accounts (FFMax/FF method)
    logger.info("\n" + "=" * 70)
    logger.info("STARTING METHOD 2: FFMax Bulk Creator (30 accounts)")
    logger.info("=" * 70)
    batch2 = method2_ffmax_accounts(30)
    all_accounts.extend(batch2)
    logger.info(f"✅ Total so far: {len(all_accounts)} accounts")

    await asyncio.sleep(10)

    # Method 3: 20 accounts (signed method - slower but reliable)
    logger.info("\n" + "=" * 70)
    logger.info("STARTING METHOD 3: Working Bulk System (20 accounts)")
    logger.info("=" * 70)
    batch3 = method3_signed_accounts(20)
    all_accounts.extend(batch3)

    logger.info("\n" + "=" * 70)
    logger.info(f"✅ TOTAL ACCOUNTS CREATED: {len(all_accounts)}")
    logger.info("=" * 70)

    # Format accounts properly
    formatted_accounts = []
    for acc in all_accounts:
        formatted_accounts.append({
            "uid": str(acc.get('uid', acc.get('account_uid', ''))),
            "password": acc.get('password', '')
        })

    return formatted_accounts


async def save_accounts(accounts: list):
    """Save accounts to file with backup"""
    # Backup existing file
    if MAIN_FILE.exists():
        with open(MAIN_FILE) as f:
            old_accounts = json.load(f)
        with open(BACKUP_FILE, 'w') as f:
            json.dump(old_accounts, f, indent=2)
        logger.info(f"📦 Backed up {len(old_accounts)} old accounts to {BACKUP_FILE}")

    # Save new accounts to separate file
    SAVE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SAVE_FILE, 'w') as f:
        json.dump(accounts, f, indent=2)

    logger.info(f"💾 Saved {len(accounts)} new accounts to {SAVE_FILE}")

    # Also update main guests_converted.json
    with open(MAIN_FILE, 'w') as f:
        json.dump(accounts, f, indent=2)

    logger.info(f"✅ Updated {MAIN_FILE} with {len(accounts)} accounts")


async def main():
    logger.info("🚀 Starting bulk account creation...")
    logger.info("Target: 100 new guest accounts")
    logger.info("Methods: temp_account_creator + ffmax_bulk_creator + working_bulk_system")
    logger.info("=" * 70 + "\n")

    accounts = await create_100_accounts()

    if len(accounts) > 0:
        await save_accounts(accounts)
        logger.info("\n" + "=" * 70)
        logger.info(f"✅ SUCCESS: Created {len(accounts)} accounts")
        logger.info(f"📁 Main file: {MAIN_FILE}")
        logger.info(f"📁 New accounts: {SAVE_FILE}")
        logger.info(f"💾 Backup: {BACKUP_FILE}")
        logger.info("=" * 70)

        # Print sample accounts
        logger.info("\n📋 Sample accounts (first 3):")
        for i, acc in enumerate(accounts[:3], 1):
            logger.info(f"   {i}. UID: {acc['uid']}, Password: {acc['password'][:20]}...")

        return True
    else:
        logger.error("❌ FAILED: No accounts created")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
