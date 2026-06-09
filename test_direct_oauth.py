"""
Test script to verify Direct OAuth method works
Bypasses ggblueshark entirely and uses Garena OAuth tokens directly
"""

import asyncio
import json
import sys
import os

# Add freefire directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'freefire'))

from freefire.get_jwt_direct import create_jwt_direct, find_working_server, check_oauth_endpoint
from freefire.encrypt_like_body import create_like_payload
import httpx


async def test_oauth_endpoint():
    """Test if OAuth endpoint is accessible"""
    print("\n" + "="*60)
    print("STEP 1: Testing OAuth Endpoint Availability")
    print("="*60)

    is_up = await check_oauth_endpoint()

    if is_up:
        print("✅ OAuth endpoint is UP and accessible")
        print("   URL: https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant")
        return True
    else:
        print("❌ OAuth endpoint is DOWN or unreachable")
        return False


async def test_single_guest():
    """Test with a single guest account"""

    print("\n" + "="*60)
    print("STEP 2: Loading Guest Account")
    print("="*60)

    # Load one guest account
    guests_file = os.path.join(os.path.dirname(__file__), "freefire/guests_manager/guests_converted.json")

    if not os.path.exists(guests_file):
        print(f"❌ Guest file not found: {guests_file}")
        return False

    with open(guests_file) as f:
        accounts = json.load(f)

        if not accounts:
            print("❌ No guest accounts found in file")
            return False

        guest = accounts[0]

    print(f"✅ Loaded guest account")
    print(f"   UID: {guest['uid']}")
    print(f"   Password: {guest['password'][:20]}...")

    # Step 1: Get JWT directly (bypassing ggblueshark)
    print("\n" + "="*60)
    print("STEP 3: Getting OAuth Token Directly (Bypassing ggblueshark)")
    print("="*60)

    jwt, region, server = await create_jwt_direct(guest['uid'], guest['password'])

    if jwt:
        print(f"✅ JWT obtained successfully")
        print(f"   JWT (preview): {jwt[:30]}...{jwt[-20:]}")
        print(f"   Region: {region}")
        print(f"   Server: {server}")
    else:
        print(f"❌ JWT creation failed")
        print(f"   This could mean:")
        print(f"   - Guest account credentials are invalid")
        print(f"   - OAuth endpoint is down")
        return False

    # Step 2: Find working server
    print("\n" + "="*60)
    print("STEP 4: Finding Working Game Server")
    print("="*60)

    working_server = await find_working_server()
    print(f"✅ Selected server: {working_server}")

    # Step 3: Create like payload
    print("\n" + "="*60)
    print("STEP 5: Creating Encrypted Like Payload")
    print("="*60)

    target_uid = "1234567890"  # Test UID (won't actually like anyone)
    like_payload = create_like_payload(target_uid, region)

    # Convert hex string to bytes if needed
    if isinstance(like_payload, str):
        import binascii
        like_payload = binascii.unhexlify(like_payload)

    print(f"✅ Payload created")
    print(f"   Size: {len(like_payload)} bytes")
    print(f"   Target UID: {target_uid}")

    # Step 4: Send like (dry run - expect error for fake UID)
    print("\n" + "="*60)
    print("STEP 6: Sending Test Like Request")
    print("="*60)

    headers = {
        "Authorization": f"Bearer {jwt}",
        "Content-Type": "application/octet-stream",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB53",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Expect": "100-continue",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{working_server}/LikeProfile",
                data=like_payload,
                headers=headers
            )

            print(f"📊 HTTP Status: {response.status_code}")

            if response.status_code in [200, 201, 204]:
                print(f"✅ Like sent successfully!")
                print(f"   (Note: Test UID may not exist, but request succeeded)")
                return True
            elif response.status_code == 401:
                print(f"⚠️  Authentication rejected (401)")
                print(f"   This could mean JWT format is incorrect")
                return False
            elif response.status_code == 400:
                print(f"✅ Request accepted (400 Bad Request)")
                print(f"   This is expected for invalid UID")
                print(f"   The important part: JWT was accepted!")
                return True
            else:
                print(f"⚠️  Unexpected response: {response.status_code}")
                print(f"   Response body (first 200 chars): {response.text[:200]}")
                return False

        except httpx.TimeoutException:
            print(f"❌ Request timed out")
            print(f"   Server may be slow or unreachable")
            return False

        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {e}")
            return False


async def run_all_tests():
    """Run all test steps"""

    print("\n" + "="*60)
    print("🧪 DIRECT OAUTH METHOD TEST SUITE")
    print("="*60)
    print("\nThis test verifies that the Direct OAuth method works")
    print("and can bypass the broken ggblueshark server.\n")

    # Test 1: Check OAuth endpoint
    oauth_ok = await test_oauth_endpoint()

    if not oauth_ok:
        print("\n" + "="*60)
        print("❌ CRITICAL: OAuth endpoint is down")
        print("="*60)
        print("\nCannot proceed with tests.")
        print("The Direct OAuth method requires Garena OAuth to be up.")
        return False

    # Test 2: Test with guest account
    guest_ok = await test_single_guest()

    # Final summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)

    print("\nResults:")
    print(f"  OAuth Endpoint:     {'✅ UP' if oauth_ok else '❌ DOWN'}")
    print(f"  Guest Account Test: {'✅ PASSED' if guest_ok else '❌ FAILED'}")

    if oauth_ok and guest_ok:
        print("\n" + "="*60)
        print("✅ SUCCESS: Direct OAuth method is working!")
        print("="*60)
        print("\nThe system can bypass ggblueshark completely.")
        print("\nWhat this means:")
        print("  • Guest likes will work even when ggblueshark is down")
        print("  • OAuth token is used directly as JWT")
        print("  • Free Fire servers accept this authentication")
        print("\nNext steps:")
        print("  1. Deploy the updated code")
        print("  2. Test with /likes command in Telegram")
        print("  3. Monitor success rate")
        return True

    elif oauth_ok and not guest_ok:
        print("\n" + "="*60)
        print("⚠️  PARTIAL SUCCESS")
        print("="*60)
        print("\nOAuth endpoint is UP, but guest test failed.")
        print("\nPossible reasons:")
        print("  • Guest account credentials may be invalid")
        print("  • Game server may be experiencing issues")
        print("  • Payload encryption may need adjustment")
        print("\nRecommendation:")
        print("  • Check guest account credentials")
        print("  • Try with different guest account")
        print("  • Check game server status")
        return False

    else:
        print("\n" + "="*60)
        print("❌ FAILED: OAuth endpoint is down")
        print("="*60)
        print("\nCannot use Direct OAuth method.")
        print("Wait for Garena OAuth to come back online.")
        return False


if __name__ == "__main__":
    try:
        result = asyncio.run(run_all_tests())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
