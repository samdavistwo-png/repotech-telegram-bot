"""Test FF MAX player info fetcher"""
import asyncio
import sys
sys.path.insert(0, '/workspace/claude-workspace/samdavistwo_gmail.com/samdavistwo-png/repotech-telegram-bot')

from freefire.ffmax_player_api import get_complete_player_info

async def main():
    uid = "1810201201"

    print(f"\n{'='*70}")
    print(f"FETCHING PLAYER INFO FOR UID: {uid}")
    print(f"{'='*70}\n")

    print("🔍 Trying all methods (FF MAX + FF + Third-party APIs)...\n")

    result = await get_complete_player_info(uid)

    print(f"\n{'='*70}")
    print("RESULT:")
    print(f"{'='*70}")
    print(f"✅ Success:       {result.get('success', False)}")
    print(f"👤 In-Game Name:  {result.get('name', 'Unknown')}")
    print(f"📊 Level:         {result.get('level', 0)}")
    print(f"❤️  Current Likes: {result.get('likes', 0)}")
    print(f"🎮 Game Type:     {result.get('game', 'Unknown')}")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    asyncio.run(main())
