"""
Guest Account Creator Tool (urllib version)
Creates fresh Free Fire guest accounts via Garena API
Works without external dependencies
"""

import json
import random
import string
import time
import urllib.request
import urllib.parse
from datetime import datetime

# Garena Configuration
GUEST_REGISTER_URL = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/register"
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
CLIENT_ID = "100067"
USER_AGENT = "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)"


def generate_device_id() -> str:
    """Generate random device ID"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))


def generate_android_id() -> str:
    """Generate random Android ID"""
    return ''.join(random.choices(string.hexdigits.lower(), k=16))


def create_single_account() -> dict:
    """Create one guest account"""
    try:
        device_id = generate_device_id()
        android_id = generate_android_id()

        payload = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "device_id": device_id,
            "android_id": android_id,
            "app_version": "1.99.3",
            "platform": "android"
        }

        headers = {
            'User-Agent': USER_AGENT,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }

        form_data = '&'.join([f"{k}={v}" for k, v in payload.items()])
        form_data_bytes = form_data.encode('utf-8')

        req = urllib.request.Request(
            GUEST_REGISTER_URL,
            data=form_data_bytes,
            headers=headers,
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=20) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))

                if data.get("code") == 0 or "uid" in data:
                    uid = str(data.get("uid", data.get("open_id", "")))
                    password = data.get("password", "")

                    if uid and password:
                        return {
                            "success": True,
                            "uid": uid,
                            "password": password
                        }

        return {"success": False, "error": "Registration failed"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def create_multiple_accounts(count: int, delay: float = 2.0):
    """
    Create multiple guest accounts with delays to avoid rate limiting

    Args:
        count: Number of accounts to create
        delay: Delay between each account creation (seconds)
    """
    accounts = []
    successful = 0
    failed = 0

    print(f"\n🚀 Creating {count} guest accounts...")
    print(f"⏱️  Delay between accounts: {delay}s")
    print(f"📊 Progress:\n")

    for i in range(count):
        result = create_single_account()

        if result.get("success"):
            accounts.append({
                "uid": result["uid"],
                "password": result["password"]
            })
            successful += 1
            print(f"✅ {i+1}/{count} - UID: {result['uid']}")
        else:
            failed += 1
            print(f"❌ {i+1}/{count} - Failed: {result.get('error', 'Unknown')}")

        # Delay to avoid rate limiting
        if i < count - 1:
            time.sleep(delay)

    print(f"\n📊 Summary:")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Success Rate: {(successful/count)*100:.1f}%")

    return accounts


def save_accounts(accounts: list, filename: str = "../freefire/accounts.json"):
    """Save accounts to JSON file"""
    data = {
        "guest_accounts": accounts,
        "created_at": datetime.now().isoformat(),
        "total_accounts": len(accounts)
    }

    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n💾 Saved {len(accounts)} accounts to {filename}")


def main():
    """Main function"""
    print("=" * 60)
    print("FREE FIRE GUEST ACCOUNT CREATOR")
    print("=" * 60)

    # Get user input
    try:
        count = int(input("\n📝 How many accounts to create? (recommended: 100-200): "))
        delay = float(input("⏱️  Delay between accounts in seconds? (recommended: 2-5): "))
    except ValueError:
        print("❌ Invalid input! Using defaults: 100 accounts, 3s delay")
        count = 100
        delay = 3.0

    # Create accounts
    accounts = create_multiple_accounts(count, delay)

    if not accounts:
        print("\n❌ No accounts created! Check if Garena API is blocking.")
        return

    # Save to file
    save_accounts(accounts)

    print("\n✅ DONE! Accounts saved to freefire/accounts.json")
    print("\n🔄 Next steps:")
    print("   1. git add freefire/accounts.json")
    print("   2. git commit -m 'Update with fresh guest accounts'")
    print("   3. git push origin main")
    print("   4. Railway will auto-deploy")


if __name__ == "__main__":
    print("\n⚠️  WARNING:")
    print("Creating many accounts rapidly may trigger Garena's anti-bot detection.")
    print("Recommended: 2-5 seconds delay between accounts.\n")

    proceed = input("Continue? (yes/no): ")
    if proceed.lower() in ['yes', 'y']:
        main()
    else:
        print("Cancelled.")
