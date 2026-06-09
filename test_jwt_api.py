#!/usr/bin/env python3
"""
Test JWT API Integration
Tests the new kaifcodec-based JWT generation system
"""

import asyncio
import json
import sys
from pathlib import Path

# Add freefire to path
sys.path.insert(0, str(Path(__file__).parent))

from freefire.get_jwt_kaifcodec import (
    create_jwt,
    create_jwt_local,
    create_jwt_with_fallback,
    JWT_API_ENDPOINTS
)

def print_header(text):
    """Print section header"""
    print()
    print("=" * 70)
    print(f" {text}")
    print("=" * 70)
    print()

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")

def print_warning(text):
    """Print warning message"""
    print(f"⚠️  {text}")

async def test_jwt_api_endpoints():
    """Test JWT API endpoint configuration"""
    print_header("JWT API Endpoints Configuration")

    if not JWT_API_ENDPOINTS:
        print_error("No JWT API endpoints configured!")
        print()
        print_info("To fix this:")
        print("  1. Set JWT_API_URL environment variable:")
        print("     export JWT_API_URL=http://localhost:3000/api/token")
        print("  2. Or deploy JWT API to Railway/Render")
        print()
        return False

    print_success(f"Found {len(JWT_API_ENDPOINTS)} configured endpoint(s):")
    for i, endpoint in enumerate(JWT_API_ENDPOINTS, 1):
        print(f"   {i}. {endpoint}")
    print()
    return True

async def test_guest_accounts():
    """Check if guest accounts are available"""
    print_header("Guest Accounts Availability")

    guests_file = Path(__file__).parent / "freefire" / "guests_manager" / "guests_converted.json"

    if not guests_file.exists():
        print_error(f"Guest accounts file not found: {guests_file}")
        print()
        print_info("To fix this:")
        print("  1. Create guest accounts using create_bulk_guests.py")
        print("  2. Or use existing accounts from guests_manager/")
        print()
        return False, []

    try:
        with open(guests_file) as f:
            accounts = json.load(f)

        if not accounts:
            print_error("Guest accounts file is empty!")
            return False, []

        print_success(f"Found {len(accounts)} guest accounts")
        print()

        # Show first account details (for testing)
        first_account = accounts[0]
        print_info("First account (for testing):")
        print(f"   UID: {first_account['uid']}")
        print(f"   Password: {'*' * len(first_account['password'])}")
        print()

        return True, accounts

    except Exception as e:
        print_error(f"Failed to load guest accounts: {e}")
        return False, []

async def test_jwt_generation_local(uid: str, password: str):
    """Test local JWT generation (fallback method)"""
    print_header("Local JWT Generation (Fallback)")

    print_info(f"Testing with UID: {uid}")
    print()

    try:
        jwt_token, region, server_url = await create_jwt_local(uid, password)

        if jwt_token:
            print_success("Local JWT generation successful!")
            print(f"   JWT Token: {jwt_token[:40]}...{jwt_token[-20:]}")
            print(f"   Region: {region}")
            print(f"   Server: {server_url}")
            print()
            return True, jwt_token
        else:
            print_error("Local JWT generation failed!")
            print()
            return False, ""

    except Exception as e:
        print_error(f"Local JWT generation error: {e}")
        print()
        return False, ""

async def test_jwt_generation_api(uid: str, password: str):
    """Test JWT API generation"""
    print_header("JWT API Generation")

    print_info(f"Testing with UID: {uid}")
    print()

    try:
        jwt_token, region, server_url = await create_jwt(uid, password)

        if jwt_token:
            print_success("JWT API generation successful!")
            print(f"   JWT Token: {jwt_token[:40]}...{jwt_token[-20:]}")
            print(f"   Region: {region}")
            print(f"   Server: {server_url}")
            print()
            return True, jwt_token
        else:
            print_warning("JWT API generation failed (API may not be running)")
            print()
            print_info("This is expected if JWT API is not yet deployed")
            print_info("The system will automatically fall back to local generation")
            print()
            return False, ""

    except Exception as e:
        print_error(f"JWT API error: {e}")
        print()
        return False, ""

async def test_jwt_generation_with_fallback(uid: str, password: str):
    """Test JWT generation with automatic fallback"""
    print_header("JWT Generation with Fallback")

    print_info(f"Testing with UID: {uid}")
    print()

    try:
        jwt_token, region, server_url = await create_jwt_with_fallback(uid, password)

        if jwt_token:
            print_success("JWT generation successful (with fallback)!")
            print(f"   JWT Token: {jwt_token[:40]}...{jwt_token[-20:]}")
            print(f"   Region: {region}")
            print(f"   Server: {server_url}")
            print()
            return True, jwt_token
        else:
            print_error("JWT generation failed even with fallback!")
            print()
            return False, ""

    except Exception as e:
        print_error(f"JWT generation error: {e}")
        print()
        return False, ""

async def run_all_tests():
    """Run all JWT API tests"""
    print()
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║           Free Fire JWT API Integration Test Suite                ║")
    print("║                   Based on kaifcodec's API                         ║")
    print("╚════════════════════════════════════════════════════════════════════╝")

    results = {
        "endpoints_configured": False,
        "guest_accounts_available": False,
        "local_jwt_works": False,
        "api_jwt_works": False,
        "fallback_jwt_works": False
    }

    # Test 1: Check endpoints configuration
    results["endpoints_configured"] = await test_jwt_api_endpoints()

    # Test 2: Check guest accounts
    accounts_ok, accounts = await test_guest_accounts()
    results["guest_accounts_available"] = accounts_ok

    if not accounts:
        print_error("Cannot proceed without guest accounts!")
        print()
        print_info("Please create guest accounts first:")
        print("  python create_bulk_guests.py")
        print()
        return results

    # Use first account for testing
    test_uid = accounts[0]["uid"]
    test_password = accounts[0]["password"]

    # Test 3: Local JWT generation (should always work)
    local_ok, local_token = await test_jwt_generation_local(test_uid, test_password)
    results["local_jwt_works"] = local_ok

    # Test 4: JWT API (may not be deployed yet)
    api_ok, api_token = await test_jwt_generation_api(test_uid, test_password)
    results["api_jwt_works"] = api_ok

    # Test 5: Fallback method (should work even if API is down)
    fallback_ok, fallback_token = await test_jwt_generation_with_fallback(test_uid, test_password)
    results["fallback_jwt_works"] = fallback_ok

    # Print summary
    print_header("Test Summary")

    print("Configuration:")
    print(f"   {'✅' if results['endpoints_configured'] else '❌'} JWT API endpoints configured")
    print(f"   {'✅' if results['guest_accounts_available'] else '❌'} Guest accounts available")
    print()

    print("JWT Generation Methods:")
    print(f"   {'✅' if results['local_jwt_works'] else '❌'} Local JWT generation")
    print(f"   {'✅' if results['api_jwt_works'] else '⚠️ '} JWT API (not critical if API not deployed)")
    print(f"   {'✅' if results['fallback_jwt_works'] else '❌'} Fallback JWT generation")
    print()

    # Overall status
    critical_tests = [
        results["guest_accounts_available"],
        results["local_jwt_works"],
        results["fallback_jwt_works"]
    ]

    if all(critical_tests):
        print_success("All critical tests passed! ✨")
        print()
        print_info("The JWT system is ready to use!")
        print()
        if not results["api_jwt_works"]:
            print_warning("JWT API is not running, but fallback is working")
            print_info("To deploy JWT API:")
            print("  1. Local: cd jwt_api && uvicorn main:app --port 3000")
            print("  2. Railway: Git push (auto-deploys)")
            print("  3. Render: Connect GitHub repo")
        print()
        return True
    else:
        print_error("Some critical tests failed!")
        print()
        print_info("Next steps:")
        if not results["guest_accounts_available"]:
            print("  1. Create guest accounts: python create_bulk_guests.py")
        if not results["local_jwt_works"]:
            print("  2. Install dependencies: pip install pycryptodome protobuf")
        if not results["fallback_jwt_works"]:
            print("  3. Check network connectivity to Garena OAuth server")
        print()
        return False

def main():
    """Main entry point"""
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print()
        print_warning("Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print()
        print_error(f"Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
