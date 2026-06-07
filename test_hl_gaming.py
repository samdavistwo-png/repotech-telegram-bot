"""
Test HL Gaming API with real credentials
Tests with UID 1810201201 (GN4-PREDATOR)
"""

import os
import urllib.request
import urllib.parse
import json

# Your HL Gaming credentials
USER_UID = "txnuOflAvIQxwFsfZ8GkTygDYcg2"
API_KEY = "pLtSopffOs6gbtxbfbYY7uCF6hWAcv"

API_BASE = "https://proapis.hlgamingofficial.com/main/games/freefire"


def test_player_info(uid: str = "1810201201"):
    """Test getting player info"""

    print(f"\n{'='*70}")
    print(f"TESTING HL GAMING API - PLAYER INFO")
    print(f"{'='*70}\n")

    print(f"Target UID: {uid}")
    print(f"Expected: GN4-PREDATOR, Level 69, ~31,113 likes\n")

    try:
        params = {
            'sectionName': 'AllData',
            'PlayerUid': uid,
            'region': 'ind',
            'useruid': USER_UID,
            'api': API_KEY
        }

        url = f"{API_BASE}/account/api"
        query_string = urllib.parse.urlencode(params)
        full_url = f"{url}?{query_string}"

        print(f"🔍 Calling API...\n")

        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json'
        }

        req = urllib.request.Request(full_url, headers=headers, method='GET')

        with urllib.request.urlopen(req, timeout=15) as response:
            print(f"✅ HTTP Status: {response.status}\n")

            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))

                # Print raw response for debugging
                print("📄 Raw API Response:")
                print(json.dumps(data, indent=2)[:500])  # First 500 chars
                print("\n")

                # Extract account info
                account_info = data.get('AccountInfo', {})
                guild_info = data.get('GuildInfo', {})

                nickname = account_info.get('nickname', account_info.get('name', ''))
                level = account_info.get('level', account_info.get('accountLevel', 1))
                likes = account_info.get('likes', account_info.get('liked', 0))
                rank = account_info.get('rank', '')
                guild_name = guild_info.get('guildName', '')

                print(f"{'='*70}")
                print("RESULT:")
                print(f"{'='*70}")
                print(f"✅ Success: YES")
                print(f"👤 Nickname: {nickname}")
                print(f"📊 Level: {level}")
                print(f"❤️  Likes: {likes:,}")
                print(f"🏆 Rank: {rank}")
                print(f"🎮 Guild: {guild_name}")
                print(f"{'='*70}\n")

                # Verify against expected
                if nickname == "GN4-PREDATOR":
                    print("✅ NAME MATCHES PERFECTLY!")
                if level == 69:
                    print("✅ LEVEL MATCHES PERFECTLY!")
                if guild_name == "GN4-BROTHERS":
                    print("✅ GUILD MATCHES PERFECTLY!")

                return True

    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.reason}")
        try:
            error_body = e.read().decode('utf-8')
            print(f"Error details: {error_body}")
        except:
            pass
        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_likes_send(target_uid: str = "1810201201", amount: int = 1):
    """Test sending likes (using 1 like for testing)"""

    print(f"\n{'='*70}")
    print(f"TESTING HL GAMING API - SEND LIKES")
    print(f"{'='*70}\n")

    print(f"Target UID: {target_uid}")
    print(f"Amount: {amount} like(s) (test mode)\n")

    try:
        params = {
            'targetUid': target_uid,
            'amount': str(amount),
            'region': 'ind',
            'useruid': USER_UID,
            'api': API_KEY
        }

        url = f"{API_BASE}/likes/api"
        query_string = urllib.parse.urlencode(params)
        full_url = f"{url}?{query_string}"

        print(f"🔍 Calling Likes API...\n")

        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json'
        }

        req = urllib.request.Request(full_url, headers=headers, method='GET')

        with urllib.request.urlopen(req, timeout=30) as response:
            print(f"✅ HTTP Status: {response.status}\n")

            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))

                print("📄 API Response:")
                print(json.dumps(data, indent=2))
                print("\n")

                print(f"{'='*70}")
                print("RESULT:")
                print(f"{'='*70}")
                print(f"✅ Likes sent successfully!")
                print(f"Amount: {amount}")
                print(f"Target: {target_uid}")
                print(f"{'='*70}\n")

                return True

    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.reason}")
        try:
            error_body = e.read().decode('utf-8')
            print(f"Error details: {error_body}")
        except:
            pass
        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "="*70)
    print("HL GAMING API TEST")
    print("="*70)
    print(f"User UID: {USER_UID}")
    print(f"API Key: {API_KEY[:10]}...")
    print("="*70)

    # Test 1: Get player info
    player_test = test_player_info("1810201201")

    if player_test:
        print("\n✅ PLAYER INFO API WORKING!\n")

        # Test 2: Send 1 test like
        # Uncomment below to test likes sending:
        # likes_test = test_likes_send("1810201201", 1)
        #
        # if likes_test:
        #     print("\n✅ LIKES SENDING API WORKING!")
        #     print("\n🎉 ALL TESTS PASSED - SYSTEM READY!")
        # else:
        #     print("\n⚠️  Likes sending failed - check API permissions")

    else:
        print("\n❌ PLAYER INFO API FAILED")
        print("\nPossible issues:")
        print("  • Invalid credentials")
        print("  • API permissions not enabled")
        print("  • Network issue")
