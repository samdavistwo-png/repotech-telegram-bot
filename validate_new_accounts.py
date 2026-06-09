"""
Validate newly created accounts
Tests if they can obtain JWT tokens and are ready for use
"""

import asyncio
import json
from pathlib import Path
import sys
import logging

# Add freefire directory to path
sys.path.insert(0, str(Path(__file__).parent / 'freefire'))

from get_jwt_alt_servers import create_jwt, get_oauth_token

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def validate_account(account: dict) -> dict:
    """Validate a single account"""
    uid = account['uid']
    password = account['password']

    result = {
        'uid': uid,
        'oauth_valid': False,
        'jwt_valid': False,
        'ready': False
    }

    # Test 1: OAuth token (should always work if account is valid)
    try:
        access_token, open_id = await get_oauth_token(uid, password)
        if access_token:
            result['oauth_valid'] = True
            result['oauth_token'] = access_token[:30] + "..."
    except Exception as e:
        result['oauth_error'] = str(e)

    # Test 2: JWT generation (tests our fallback system)
    try:
        jwt_token, region, server_url = await create_jwt(uid, password)
        if jwt_token:
            result['jwt_valid'] = True
            result['jwt_token'] = jwt_token[:30] + "..."
            result['region'] = region
            result['server_url'] = server_url
    except Exception as e:
        result['jwt_error'] = str(e)

    # Account is ready if JWT can be obtained
    result['ready'] = result['jwt_valid']

    return result


async def validate_all_accounts():
    """Validate all newly created accounts"""
    # Try new accounts file first, fall back to main file
    new_accounts_file = Path(__file__).parent / "freefire" / "guests_manager" / "new_guests_2026.json"
    main_accounts_file = Path(__file__).parent / "freefire" / "guests_manager" / "guests_converted.json"

    if new_accounts_file.exists():
        accounts_file = new_accounts_file
        logger.info(f"📁 Validating new accounts from: {accounts_file}")
    elif main_accounts_file.exists():
        accounts_file = main_accounts_file
        logger.info(f"📁 Validating accounts from: {accounts_file}")
    else:
        logger.error("❌ No accounts file found")
        return

    with open(accounts_file) as f:
        accounts = json.load(f)

    logger.info(f"🔍 Validating {len(accounts)} accounts...")
    logger.info("=" * 70)

    results = []
    for i, account in enumerate(accounts):
        print(f"[{i+1}/{len(accounts)}] Testing UID {account['uid']}...", end=" ", flush=True)
        result = await validate_account(account)
        results.append(result)

        if result['ready']:
            print("✅ READY")
        elif result['oauth_valid']:
            print("⚠️  OAuth OK, JWT Failed")
        else:
            print("❌ FAILED")

        # Rate limiting
        await asyncio.sleep(1)

    # Summary
    oauth_valid = sum(1 for r in results if r['oauth_valid'])
    jwt_valid = sum(1 for r in results if r['jwt_valid'])
    ready = sum(1 for r in results if r['ready'])

    print("\n" + "=" * 70)
    print(f"📊 VALIDATION RESULTS:")
    print(f"   Total Accounts: {len(accounts)}")
    print(f"   OAuth Valid: {oauth_valid}/{len(accounts)} ({oauth_valid/len(accounts)*100:.1f}%)")
    print(f"   JWT Valid: {jwt_valid}/{len(accounts)} ({jwt_valid/len(accounts)*100:.1f}%)")
    print(f"   Ready to Use: {ready}/{len(accounts)} ({ready/len(accounts)*100:.1f}%)")
    print("=" * 70)

    # Save results
    results_file = Path(__file__).parent / "validation_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "total": len(accounts),
            "oauth_valid": oauth_valid,
            "jwt_valid": jwt_valid,
            "ready": ready,
            "accounts": results
        }, f, indent=2)

    logger.info(f"\n💾 Detailed results saved to: {results_file}")

    # Show failed accounts
    failed_accounts = [r for r in results if not r['ready']]
    if failed_accounts:
        print(f"\n⚠️  FAILED ACCOUNTS ({len(failed_accounts)}):")
        for r in failed_accounts[:5]:  # Show first 5
            print(f"   - UID: {r['uid']}")
            if 'oauth_error' in r:
                print(f"     OAuth Error: {r['oauth_error']}")
            if 'jwt_error' in r:
                print(f"     JWT Error: {r['jwt_error']}")
        if len(failed_accounts) > 5:
            print(f"   ... and {len(failed_accounts) - 5} more")

    return {
        "total": len(accounts),
        "ready": ready,
        "success_rate": ready / len(accounts) * 100
    }


async def test_sample_account():
    """Test a single sample account from the file"""
    accounts_file = Path(__file__).parent / "freefire" / "guests_manager" / "guests_converted.json"

    if not accounts_file.exists():
        logger.error("❌ No accounts file found")
        return

    with open(accounts_file) as f:
        accounts = json.load(f)

    if not accounts:
        logger.error("❌ No accounts in file")
        return

    # Test first account
    sample = accounts[0]
    logger.info(f"\n🧪 Testing sample account: {sample['uid']}")
    logger.info("=" * 70)

    result = await validate_account(sample)

    logger.info(f"\n📊 RESULTS:")
    logger.info(f"   OAuth Valid: {'✅' if result['oauth_valid'] else '❌'}")
    logger.info(f"   JWT Valid: {'✅' if result['jwt_valid'] else '❌'}")
    logger.info(f"   Ready to Use: {'✅' if result['ready'] else '❌'}")

    if result['ready']:
        logger.info(f"\n✅ SUCCESS! Account is ready to use.")
        logger.info(f"   Region: {result.get('region', 'N/A')}")
        logger.info(f"   Server: {result.get('server_url', 'N/A')}")
    else:
        logger.error(f"\n❌ FAILED! Account is not ready.")
        if 'oauth_error' in result:
            logger.error(f"   OAuth Error: {result['oauth_error']}")
        if 'jwt_error' in result:
            logger.error(f"   JWT Error: {result['jwt_error']}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--sample":
        # Test just one account
        asyncio.run(test_sample_account())
    else:
        # Validate all accounts
        asyncio.run(validate_all_accounts())
