"""
Test JWT Fallback System
Verifies that the new authentication system works with existing accounts
"""

import asyncio
import json
from pathlib import Path
import sys

# Add freefire directory to path
sys.path.insert(0, str(Path(__file__).parent / 'freefire'))

from get_jwt_alt_servers import (
    create_jwt,
    get_oauth_token,
    ALTERNATIVE_LOGIN_SERVERS
)

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_existing_account():
    """Test the JWT fallback system with an existing account"""
    accounts_file = Path(__file__).parent / "freefire" / "guests_manager" / "guests_converted.json"

    if not accounts_file.exists():
        logger.error("❌ No accounts file found")
        return False

    with open(accounts_file) as f:
        accounts = json.load(f)

    if not accounts:
        logger.error("❌ No accounts in file")
        return False

    # Test with first account
    test_account = accounts[0]
    uid = test_account['uid']
    password = test_account['password']

    logger.info(f"\n{'='*70}")
    logger.info(f"Testing JWT Fallback System")
    logger.info(f"{'='*70}")
    logger.info(f"Test Account UID: {uid}")
    logger.info(f"Alternative servers: {len(ALTERNATIVE_LOGIN_SERVERS)}")
    logger.info("")

    # Step 1: Test OAuth token
    logger.info("Step 1: Testing OAuth token...")
    access_token, open_id = await get_oauth_token(uid, password)

    if access_token:
        logger.info(f"✅ OAuth token obtained successfully")
        logger.info(f"   Token: {access_token[:30]}...")
        logger.info(f"   Open ID: {open_id}")
    else:
        logger.error(f"❌ OAuth token failed")
        return False

    # Step 2: Test JWT with fallback
    logger.info("\nStep 2: Testing JWT with fallback system...")
    jwt_token, region, server_url = await create_jwt(uid, password)

    if jwt_token:
        logger.info(f"✅ JWT obtained successfully")
        logger.info(f"   JWT: {jwt_token[:30]}...")
        logger.info(f"   Region: {region}")
        logger.info(f"   Server URL: {server_url}")
    else:
        logger.error(f"❌ JWT generation failed")
        return False

    logger.info(f"\n{'='*70}")
    logger.info(f"✅ SUCCESS! JWT fallback system is working")
    logger.info(f"{'='*70}")

    return True


async def test_multiple_accounts(count: int = 5):
    """Test JWT fallback with multiple accounts"""
    accounts_file = Path(__file__).parent / "freefire" / "guests_manager" / "guests_converted.json"

    if not accounts_file.exists():
        logger.error("❌ No accounts file found")
        return

    with open(accounts_file) as f:
        accounts = json.load(f)

    test_accounts = accounts[:min(count, len(accounts))]

    logger.info(f"\n{'='*70}")
    logger.info(f"Testing {len(test_accounts)} accounts with JWT fallback")
    logger.info(f"{'='*70}\n")

    success = 0
    failed = 0

    for i, account in enumerate(test_accounts, 1):
        uid = account['uid']
        password = account['password']

        print(f"[{i}/{len(test_accounts)}] Testing UID {uid}...", end=" ", flush=True)

        try:
            jwt_token, region, server_url = await create_jwt(uid, password)
            if jwt_token:
                print("✅")
                success += 1
            else:
                print("❌")
                failed += 1
        except Exception as e:
            print(f"❌ Error: {e}")
            failed += 1

        await asyncio.sleep(1)  # Rate limiting

    logger.info(f"\n{'='*70}")
    logger.info(f"Results: {success}/{len(test_accounts)} successful ({success/len(test_accounts)*100:.1f}%)")
    logger.info(f"{'='*70}")

    return success == len(test_accounts)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--multi":
        # Test multiple accounts
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        asyncio.run(test_multiple_accounts(count))
    else:
        # Test single account
        asyncio.run(test_existing_account())
