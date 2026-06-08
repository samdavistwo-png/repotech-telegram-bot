#!/usr/bin/env python3
"""
Environment Variable Verification Script
Checks if all required environment variables are set correctly
"""

import os
from dotenv import load_dotenv

# Load .env file (for local testing only)
load_dotenv()

def verify_env_vars():
    """Verify all required environment variables"""

    print("=" * 60)
    print("🔍 ENVIRONMENT VARIABLE VERIFICATION")
    print("=" * 60)
    print()

    required_vars = {
        "BOT_TOKEN": "Telegram Bot Token (from @BotFather)",
        "ADMIN_ID": "Your Telegram User ID",
        "UPI_ID": "UPI ID for payments",
        "HL_GAMING_USERUID": "HL Gaming Developer UID",
        "HL_GAMING_API_KEY": "HL Gaming API Key"
    }

    missing_vars = []
    found_vars = []

    for var_name, description in required_vars.items():
        value = os.getenv(var_name)

        if value:
            # Mask sensitive values
            if var_name in ["BOT_TOKEN", "HL_GAMING_API_KEY"]:
                masked_value = value[:10] + "..." + value[-10:] if len(value) > 20 else "*" * len(value)
            else:
                masked_value = value

            print(f"✅ {var_name}: {masked_value}")
            found_vars.append(var_name)
        else:
            print(f"❌ {var_name}: NOT SET")
            print(f"   Description: {description}")
            missing_vars.append(var_name)

        print()

    print("=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Found: {len(found_vars)}/{len(required_vars)}")
    print(f"❌ Missing: {len(missing_vars)}/{len(required_vars)}")
    print()

    if missing_vars:
        print("⚠️  MISSING VARIABLES:")
        for var in missing_vars:
            print(f"   - {var}")
        print()
        print("📝 ACTION REQUIRED:")
        print("   1. Go to Railway Dashboard → Variables")
        print("   2. Add the missing environment variables")
        print("   3. Railway will automatically redeploy")
        print()
        return False
    else:
        print("✅ All required environment variables are set!")
        print()
        return True

if __name__ == "__main__":
    success = verify_env_vars()
    exit(0 if success else 1)
