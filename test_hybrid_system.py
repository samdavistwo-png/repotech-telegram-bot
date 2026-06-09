#!/usr/bin/env python3
"""
Test script for the Hybrid Likes System
Tests guest likes engine and hybrid handler integration
"""

import asyncio
import sys
import os

# Add freefire directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'freefire'))

from guest_likes_engine import (
    load_usage,
    save_usage,
    ensure_target,
    guest_used_for_target,
    get_available_guests,
    send_likes_with_guests
)


async def test_guest_system():
    """Test guest likes engine functionality"""
    print("=" * 60)
    print("HYBRID LIKES SYSTEM TEST")
    print("=" * 60)

    # Test 1: Load usage
    print("\n[1] Testing usage tracking system...")
    load_usage()
    print("✅ Usage system loaded successfully")

    # Test 2: Check guest availability
    test_uid = "1234567890"  # Dummy UID for testing
    print(f"\n[2] Checking available guests for UID: {test_uid}")
    available = get_available_guests(test_uid)
    print(f"✅ Available guests: {available}")

    # Test 3: Ensure target
    print(f"\n[3] Initializing target UID: {test_uid}")
    ensure_target(test_uid)
    print("✅ Target initialized in usage tracker")

    # Test 4: Check if specific guest is used
    test_guest_uid = "4103677597"  # First guest from file
    print(f"\n[4] Checking if guest {test_guest_uid} is used for {test_uid}")
    is_used = guest_used_for_target(test_uid, test_guest_uid)
    print(f"✅ Guest used status: {is_used}")

    # Test 5: Display summary
    print("\n" + "=" * 60)
    print("SYSTEM SUMMARY")
    print("=" * 60)
    print(f"Total available guests for new targets: {available}")
    print(f"Usage tracking file: usage_history/guest_usage_by_target.json")
    print(f"Guest accounts file: freefire/guests_manager/guests_converted.json")
    print("\n✅ All basic tests passed!")
    print("\n⚠️  Note: Full like sending test skipped (requires real UID)")
    print("    Use the /likes command in Telegram to test end-to-end")

    return True


async def test_integration():
    """Test integration points"""
    print("\n" + "=" * 60)
    print("INTEGRATION TEST")
    print("=" * 60)

    try:
        # Test import of hybrid handler
        print("\n[1] Testing hybrid handler import...")
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'handlers'))
        from likes_hybrid import likes_hybrid_handler
        print("✅ Hybrid handler imported successfully")

        # Test import of HL Gaming fallback
        print("\n[2] Testing HL Gaming fallback import...")
        from hl_gaming_likes_api import send_likes_hl_gaming
        from hl_gaming_player_api import get_player_info_hl_gaming
        print("✅ HL Gaming APIs imported successfully")

        # Test import of count_likes
        print("\n[3] Testing count_likes import...")
        from count_likes import GetAccountInformation
        print("✅ count_likes imported successfully")

        print("\n✅ All integration tests passed!")
        return True

    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        return False


async def main():
    """Run all tests"""
    try:
        # Run guest system tests
        result1 = await test_guest_system()

        # Run integration tests
        result2 = await test_integration()

        if result1 and result2:
            print("\n" + "=" * 60)
            print("🎉 ALL TESTS PASSED!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Start the bot: python3 bot.py")
            print("2. Test with /likes command in Telegram")
            print("3. Monitor logs for guest/fallback behavior")
            print("\nExpected behavior:")
            print("• First 50-161 likes per target: Guest accounts (FREE)")
            print("• After guest exhaustion: HL Gaming fallback (PREMIUM)")
            print("• Smart automatic switching between methods")
            return 0
        else:
            print("\n❌ Some tests failed!")
            return 1

    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
