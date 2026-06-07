"""
Free Fire MAX Player Info API
Fetches real player names from both FF and FF MAX
"""

import httpx
import logging
from typing import Dict

logger = logging.getLogger(__name__)


async def get_player_info_ffmax_method1(uid: str) -> Dict:
    """Method 1: FF MAX Garena antispam API"""
    try:
        url = "https://ffmax.garena.com/api/antispam/get_user_basic_info"
        payload = {"uid": uid, "region": "IND"}

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    user = data.get("data", {})
                    return {
                        "success": True,
                        "name": user.get("nickname", ""),
                        "likes": user.get("liked", 0),
                        "level": user.get("level", 1),
                        "game": "FF MAX"
                    }
    except Exception as e:
        logger.debug(f"FFMAX Method 1 failed: {e}")

    return {"success": False}


async def get_player_info_ffmax_method2(uid: str) -> Dict:
    """Method 2: FF MAX profile API"""
    try:
        url = f"https://ffmax.garena.com/api/profile/{uid}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "name": data.get("nickname", data.get("name", "")),
                    "likes": data.get("liked", 0),
                    "level": data.get("level", 1),
                    "game": "FF MAX"
                }
    except Exception as e:
        logger.debug(f"FFMAX Method 2 failed: {e}")

    return {"success": False}


async def get_player_info_ff_method1(uid: str) -> Dict:
    """Method 3: Regular FF Garena antispam API"""
    try:
        url = "https://ff.garena.com/api/antispam/get_user_basic_info"
        payload = {"uid": uid, "region": "IND"}

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    user = data.get("data", {})
                    return {
                        "success": True,
                        "name": user.get("nickname", ""),
                        "likes": user.get("liked", 0),
                        "level": user.get("level", 1),
                        "game": "FF"
                    }
    except Exception as e:
        logger.debug(f"FF Method 1 failed: {e}")

    return {"success": False}


async def get_player_info_ff_method2(uid: str) -> Dict:
    """Method 4: Regular FF profile API"""
    try:
        url = f"https://ff.garena.com/api/profile/{uid}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "name": data.get("nickname", data.get("name", "")),
                    "likes": data.get("liked", 0),
                    "level": data.get("level", 1),
                    "game": "FF"
                }
    except Exception as e:
        logger.debug(f"FF Method 2 failed: {e}")

    return {"success": False}


async def get_player_info_alternative(uid: str) -> Dict:
    """Method 5: Alternative third-party API"""
    try:
        # Try multiple third-party APIs
        apis = [
            f"https://freefireinfo.site/api/info/sg/{uid}",
            f"https://api-freefire.vercel.app/api/profile/{uid}",
            f"https://ff-api.com/player/{uid}"
        ]

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }

        for api_url in apis:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(api_url, headers=headers)

                    if response.status_code == 200:
                        data = response.json()

                        # Try different field names
                        name = data.get("nickname") or data.get("name") or data.get("accountName") or data.get("playerName") or ""
                        likes = data.get("likes") or data.get("liked") or 0
                        level = data.get("level") or 1

                        if name:
                            return {
                                "success": True,
                                "name": name,
                                "likes": likes,
                                "level": level,
                                "game": "FF/MAX (Third-party)"
                            }
            except:
                continue

    except Exception as e:
        logger.debug(f"Alternative API failed: {e}")

    return {"success": False}


async def get_complete_player_info(uid: str) -> Dict:
    """
    Get complete player info trying all methods for both FF and FF MAX

    Returns:
        Dict with success, name, likes, level, game
    """
    # Try FF MAX first (most likely for newer accounts)
    result = await get_player_info_ffmax_method1(uid)
    if result.get("success") and result.get("name"):
        logger.info(f"✅ Got player info via FF MAX Method 1: {result.get('name')}")
        return result

    result = await get_player_info_ffmax_method2(uid)
    if result.get("success") and result.get("name"):
        logger.info(f"✅ Got player info via FF MAX Method 2: {result.get('name')}")
        return result

    # Try regular FF
    result = await get_player_info_ff_method1(uid)
    if result.get("success") and result.get("name"):
        logger.info(f"✅ Got player info via FF Method 1: {result.get('name')}")
        return result

    result = await get_player_info_ff_method2(uid)
    if result.get("success") and result.get("name"):
        logger.info(f"✅ Got player info via FF Method 2: {result.get('name')}")
        return result

    # Try alternative APIs
    result = await get_player_info_alternative(uid)
    if result.get("success") and result.get("name"):
        logger.info(f"✅ Got player info via Alternative API: {result.get('name')}")
        return result

    # All methods failed
    logger.warning(f"⚠️ All methods failed for UID {uid}")
    return {
        "success": False,
        "name": f"Player-{uid[-6:]}",
        "likes": 0,
        "level": 1,
        "game": "Unknown"
    }
