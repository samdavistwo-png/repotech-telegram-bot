"""
Guest Account Creator Tool
Creates fresh Free Fire guest accounts via Garena API

Run this script to generate new guest accounts for accounts.json
"""

import httpx
import asyncio
import json
import random
import string
import sys
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


async def create_single_account() -> dict:
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

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                GUEST_REGISTER_URL,
                data=form_data,
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()

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


async def create_multiple_accounts(count: int, delay: float = 2.0):
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
        result = await create_single_account()

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
            await asyncio.sleep(delay)

    print(f"\n📊 Summary:")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Success Rate: {(successful/count)*100:.1f}%")

    return accounts


async def save_accounts(accounts: list, filename: str = "../freefire/accounts.json"):
    """Save accounts to JSON file"""
    data = {
        "guest_accounts": accounts,
        "created_at": datetime.now().isoformat(),
        "total_accounts": len(accounts)
    }

    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n💾 Saved {len(accounts)} accounts to {filename}")


async def main():
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
    accounts = await create_multiple_accounts(count, delay)

    if not accounts:
        print("\n❌ No accounts created! Check if Garena API is blocking.")
        return

    # Save to file
    await save_accounts(accounts)

    print("\n✅ DONE! Accounts saved to freefire/accounts.json")
    print("\n🔄 Restart your bot to use the new accounts.")


if __name__ == "__main__":
    print("\n⚠️  WARNING:")
    print("Creating many accounts rapidly may trigger Garena's anti-bot detection.")
    print("Recommended: 2-5 seconds delay between accounts.\n")

    proceed = input("Continue? (yes/no): ")
    if proceed.lower() in ['yes', 'y']:
        asyncio.run(main())
    else:
        print("Cancelled.")
