"""
Simple Bulk Guest Account Creator
Creates 100 new Free Fire guest accounts using urllib (no httpx needed)
"""

import json
import time
import sys
from pathlib import Path

# Add freefire directory to path
sys.path.insert(0, str(Path(__file__).parent / 'freefire'))

from ffmax_bulk_creator import create_guest_account

# File paths
SAVE_FILE = Path(__file__).parent / "freefire" / "guests_manager" / "new_guests_2026.json"
BACKUP_FILE = Path(__file__).parent / "freefire" / "guests_manager" / "guests_converted.backup.json"
MAIN_FILE = Path(__file__).parent / "freefire" / "guests_manager" / "guests_converted.json"


def create_bulk_accounts_simple(target_count: int = 100, delay: float = 3.0):
    """
    Create bulk accounts using ffmax_bulk_creator (uses urllib, no httpx needed)

    Args:
        target_count: Number of accounts to create
        delay: Delay between creations to avoid rate limiting
    """
    accounts = []
    successful = 0
    failed = 0

    print(f"\n{'='*70}")
    print(f"CREATING {target_count} FREE FIRE GUEST ACCOUNTS")
    print(f"{'='*70}")
    print(f"⏱️  Delay: {delay}s between accounts")
    print(f"🎮 Method: ffmax_bulk_creator (urllib)")
    print(f"\n📊 Progress:\n")

    for i in range(1, target_count + 1):
        print(f"[{i}/{target_count}] Creating account #{i}...", end=" ", flush=True)

        # Use regular FF (not FFMax) for broader compatibility
        result = create_guest_account(i, use_ffmax=False)

        if result.get("success"):
            uid = result["uid"]
            password = result["password"]

            accounts.append({
                "uid": uid,
                "password": password
            })
            successful += 1
            print("✅")
        else:
            failed += 1
            error_msg = result.get('error', 'Unknown')
            print(f"❌ {error_msg}")

        # Delay to avoid rate limiting (skip on last iteration)
        if i < target_count:
            time.sleep(delay)

    print(f"\n{'='*70}")
    print(f"📊 SUMMARY:")
    print(f"   ✅ Successful: {successful}/{target_count}")
    print(f"   ❌ Failed: {failed}/{target_count}")
    print(f"   📈 Success Rate: {(successful/target_count)*100:.1f}%")
    print(f"{'='*70}\n")

    return accounts


def save_accounts(accounts: list):
    """Save accounts to file with backup"""
    if not accounts:
        print("❌ No accounts to save")
        return False

    # Backup existing file
    if MAIN_FILE.exists():
        with open(MAIN_FILE) as f:
            old_accounts = json.load(f)
        with open(BACKUP_FILE, 'w') as f:
            json.dump(old_accounts, f, indent=2)
        print(f"📦 Backed up {len(old_accounts)} old accounts to {BACKUP_FILE}")

    # Save new accounts to separate file
    SAVE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SAVE_FILE, 'w') as f:
        json.dump(accounts, f, indent=2)

    print(f"💾 Saved {len(accounts)} new accounts to {SAVE_FILE}")

    # Also update main guests_converted.json
    with open(MAIN_FILE, 'w') as f:
        json.dump(accounts, f, indent=2)

    print(f"✅ Updated {MAIN_FILE} with {len(accounts)} accounts")
    return True


def main():
    print("🚀 Simple Bulk Account Creator")
    print("Uses urllib only (no external dependencies)")
    print("=" * 70 + "\n")

    # Configuration
    target_count = 100
    delay = 3.0  # seconds between accounts

    print(f"Target: {target_count} accounts")
    print(f"Delay: {delay}s between creations")
    print(f"Method: Free Fire guest registration (Garena API)")
    print("\n⚠️  This will take approximately {:.1f} minutes".format((target_count * delay) / 60))

    # Confirm
    try:
        response = input("\nProceed? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Cancelled.")
            return False
    except EOFError:
        # Running in automated mode
        print("Running in automated mode...")

    print("\nStarting account creation...\n")

    # Create accounts
    accounts = create_bulk_accounts_simple(target_count, delay)

    # Save accounts
    if accounts:
        success = save_accounts(accounts)

        if success:
            print("\n" + "=" * 70)
            print(f"✅ SUCCESS: Created {len(accounts)} accounts")
            print(f"📁 Main file: {MAIN_FILE}")
            print(f"📁 New accounts: {SAVE_FILE}")
            print(f"💾 Backup: {BACKUP_FILE}")
            print("=" * 70)

            # Print sample accounts
            print("\n📋 Sample accounts (first 3):")
            for i, acc in enumerate(accounts[:3], 1):
                print(f"   {i}. UID: {acc['uid']}, Password: {acc['password'][:20]}...")

            return True
    else:
        print("\n❌ FAILED: No accounts created")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
