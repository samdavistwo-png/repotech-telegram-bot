"""
Quick verification script to check Direct OAuth implementation
Checks file structure and imports without running actual API calls
"""

import os
import sys


def check_file_exists(filepath):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {filepath}")
        return True
    else:
        print(f"❌ {filepath} - NOT FOUND")
        return False


def check_import_in_file(filepath, old_import, new_import):
    """Check if import was updated correctly"""
    if not os.path.exists(filepath):
        print(f"❌ {filepath} - FILE NOT FOUND")
        return False

    with open(filepath, 'r') as f:
        content = f.read()

    if new_import in content:
        print(f"✅ {filepath} - Using new Direct OAuth import")
        return True
    elif old_import in content and new_import not in content:
        print(f"⚠️  {filepath} - Still using old import")
        return False
    else:
        print(f"⚠️  {filepath} - Cannot determine import status")
        return False


def check_function_exists(filepath, function_name):
    """Check if a function is defined in a file"""
    if not os.path.exists(filepath):
        print(f"❌ {filepath} - FILE NOT FOUND")
        return False

    with open(filepath, 'r') as f:
        content = f.read()

    if f"def {function_name}" in content or f"async def {function_name}" in content:
        print(f"✅ {filepath} - Function '{function_name}' found")
        return True
    else:
        print(f"❌ {filepath} - Function '{function_name}' NOT FOUND")
        return False


def main():
    print("="*60)
    print("DIRECT OAUTH IMPLEMENTATION VERIFICATION")
    print("="*60)
    print()

    all_checks_passed = True

    # Check 1: New files created
    print("1️⃣ Checking new files...")
    files_ok = True
    files_ok &= check_file_exists("freefire/get_jwt_direct.py")
    files_ok &= check_file_exists("test_direct_oauth.py")
    files_ok &= check_file_exists("DIRECT_OAUTH_IMPLEMENTATION.md")
    files_ok &= check_file_exists("MIGRATION_SUMMARY.md")
    all_checks_passed &= files_ok
    print()

    # Check 2: Core functions in get_jwt_direct.py
    print("2️⃣ Checking core functions in get_jwt_direct.py...")
    functions_ok = True
    functions_ok &= check_function_exists("freefire/get_jwt_direct.py", "get_access_token")
    functions_ok &= check_function_exists("freefire/get_jwt_direct.py", "create_jwt_direct")
    functions_ok &= check_function_exists("freefire/get_jwt_direct.py", "find_working_server")
    functions_ok &= check_function_exists("freefire/get_jwt_direct.py", "check_oauth_endpoint")
    all_checks_passed &= functions_ok
    print()

    # Check 3: Import updated in guest_likes_engine.py
    print("3️⃣ Checking import in guest_likes_engine.py...")
    import_ok = check_import_in_file(
        "freefire/guest_likes_engine.py",
        "from get_jwt import create_jwt",
        "from get_jwt_direct import create_jwt_direct as create_jwt"
    )
    all_checks_passed &= import_ok
    print()

    # Check 4: Import added to likes_hybrid.py
    print("4️⃣ Checking OAuth check in likes_hybrid.py...")
    with open("handlers/likes_hybrid.py", 'r') as f:
        content = f.read()

    if "from get_jwt_direct import check_oauth_endpoint" in content:
        print("✅ handlers/likes_hybrid.py - OAuth endpoint check import added")
        hybrid_ok = True
    else:
        print("❌ handlers/likes_hybrid.py - OAuth endpoint check import MISSING")
        hybrid_ok = False

    if "oauth_working = await check_oauth_endpoint()" in content:
        print("✅ handlers/likes_hybrid.py - OAuth health check implemented")
    else:
        print("⚠️  handlers/likes_hybrid.py - OAuth health check may be missing")
        hybrid_ok = False

    all_checks_passed &= hybrid_ok
    print()

    # Check 5: API health check updated
    print("5️⃣ Checking API health check updates...")
    with open("handlers/apihealth.py", 'r') as f:
        content = f.read()

    health_ok = True
    if "Garena OAuth (Direct Method)" in content:
        print("✅ handlers/apihealth.py - OAuth Direct Method endpoint added")
    else:
        print("❌ handlers/apihealth.py - OAuth Direct Method endpoint MISSING")
        health_ok = False

    if "LEGACY SERVICE DOWN (OK)" in content:
        print("✅ handlers/apihealth.py - New status messages added")
    else:
        print("⚠️  handlers/apihealth.py - New status messages may be missing")
        health_ok = False

    all_checks_passed &= health_ok
    print()

    # Check 6: Guest accounts file exists
    print("6️⃣ Checking guest accounts file...")
    guests_file = "freefire/guests_manager/guests_converted.json"
    if os.path.exists(guests_file):
        import json
        with open(guests_file, 'r') as f:
            guests = json.load(f)
        print(f"✅ {guests_file} - {len(guests)} guest accounts found")
        if len(guests) > 0:
            print(f"   Sample guest UID: {guests[0].get('uid', 'N/A')}")
    else:
        print(f"⚠️  {guests_file} - NOT FOUND (may be created later)")
    print()

    # Final summary
    print("="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    print()

    if all_checks_passed:
        print("✅ ALL CHECKS PASSED!")
        print()
        print("Implementation is complete. Ready to deploy.")
        print()
        print("Next steps:")
        print("1. Commit and push changes")
        print("2. Deploy to production")
        print("3. Run /apihealth in Telegram to verify")
        print("4. Test /likes command with a real UID")
        return 0
    else:
        print("⚠️  SOME CHECKS FAILED")
        print()
        print("Please review the errors above and fix them.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
