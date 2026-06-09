# Protective Source License v1.0 (PSL-1.0)
# Copyright (c) 2025 Kaif
# Unauthorized removal of credits or use for abusive/illegal purposes
# will terminate all rights granted under this license.

"""
Guest Likes Engine - Free method for sending Free Fire likes
Uses 100+ guest accounts to send likes directly to Garena servers
Each guest can like a target UID once (permanent tracking per target)
"""

import httpx
import asyncio
import binascii
import json
import os
import time
import logging
from pathlib import Path
from typing import Dict, Tuple

# Import from existing modules
# OLD: from get_jwt import create_jwt  # Uses ggblueshark - BROKEN
# OLD: from get_jwt_direct import create_jwt_direct as create_jwt  # Direct OAuth only
# OLD: from get_jwt_alt_servers import create_jwt  # Fallback method (multiple servers)
# NEW: Use kaifcodec's JWT API approach - working JWT generator
from get_jwt_kaifcodec import create_jwt_with_fallback as create_jwt
from encrypt_like_body import create_like_payload

logger = logging.getLogger(__name__)

# Paths (relative to freefire directory)
SCRIPT_DIR = Path(__file__).parent
GUESTS_FILE = SCRIPT_DIR / "guests_manager" / "guests_converted.json"
USAGE_DIR = SCRIPT_DIR.parent / "usage_history"
USAGE_FILE = USAGE_DIR / "guest_usage_by_target.json"

# Constants
MAX_CONCURRENT = 20  # 20 concurrent guest requests at a time
RELEASEVERSION = "OB53"

# Ensure usage directory exists
USAGE_DIR.mkdir(parents=True, exist_ok=True)

# Global usage tracker (loaded from JSON)
_usage_by_target: Dict = {}
_usage_lock = asyncio.Lock()


def load_usage():
    """Load usage history from JSON file"""
    global _usage_by_target
    if USAGE_FILE.exists():
        with open(USAGE_FILE, "r") as f:
            _usage_by_target = json.load(f)
            logger.info(f"Loaded guest usage for {len(_usage_by_target)} targets")
    else:
        _usage_by_target = {}
        logger.info("Created new guest usage tracker")


async def save_usage():
    """Save usage history to JSON file (thread-safe with atomic write)"""
    async with _usage_lock:
        # Atomic write: write to temp file first
        temp_file = USAGE_FILE.with_suffix('.tmp')
        with open(temp_file, "w") as f:
            json.dump(_usage_by_target, f, indent=2)
        # Atomic rename
        temp_file.replace(USAGE_FILE)
        logger.debug(f"Saved guest usage to {USAGE_FILE}")


def ensure_target(target_uid: str):
    """Initialize target in usage tracker if not exists"""
    if target_uid not in _usage_by_target:
        _usage_by_target[target_uid] = {
            "used_guests": {},
            "total_likes": 0
        }


def guest_used_for_target(target_uid: str, guest_uid: str) -> bool:
    """Check if guest has already liked this target"""
    ensure_target(target_uid)
    return guest_uid in _usage_by_target[target_uid]["used_guests"]


def mark_used(target_uid: str, guest_uid: str, timestamp_ms: int):
    """Mark guest as used for this target"""
    ensure_target(target_uid)
    _usage_by_target[target_uid]["used_guests"][guest_uid] = timestamp_ms
    _usage_by_target[target_uid]["total_likes"] = len(_usage_by_target[target_uid]["used_guests"])


def get_available_guests(target_uid: str) -> int:
    """Get count of available (unused) guests for this target"""
    ensure_target(target_uid)
    if not GUESTS_FILE.exists():
        return 0

    with open(GUESTS_FILE, "r") as f:
        all_guests = json.load(f)

    used_count = len(_usage_by_target[target_uid]["used_guests"])
    return len(all_guests) - used_count


def get_base_url(region: str) -> str:
    """Determine base URL based on region"""
    region_upper = region.upper()
    if region_upper == "IND":
        return "https://client.ind.freefiremobile.com"
    elif region_upper in {"BR", "US", "SAC", "NA"}:
        return "https://client.us.freefiremobile.com"
    else:
        return "https://clientbp.ggblueshark.com"


async def like_with_guest(
    guest: dict,
    target_uid: str,
    base_url: str,
    semaphore: asyncio.Semaphore
) -> Tuple[bool, str]:
    """
    Send a like using a single guest account

    Returns:
        (success: bool, error_message: str)
    """
    guest_uid = str(guest["uid"])
    guest_pass = guest["password"]
    now_ms = int(time.time() * 1000)

    # Check if guest already used for this target
    if guest_used_for_target(target_uid, guest_uid):
        logger.debug(f"Guest {guest_uid} already used for target {target_uid}")
        return False, "already_used"

    async with semaphore:
        try:
            # Create JWT for guest account
            jwt, region, server_url = await create_jwt(guest_uid, guest_pass)

            # Create encrypted payload
            payload = create_like_payload(target_uid, region)
            if isinstance(payload, str):
                payload = binascii.unhexlify(payload)

            headers = {
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 14; Pixel 8 Build/UP1A.231005.007)",
                "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip",
                "Content-Type": "application/octet-stream",
                "Expect": "100-continue",
                "Authorization": f"Bearer {jwt}",
                "X-Unity-Version": "2018.4.11f1",
                "X-GA": "v1 1",
                "ReleaseVersion": RELEASEVERSION,
            }

            # Send like request
            async with httpx.AsyncClient() as client:
                url = f"{base_url}/LikeProfile"
                response = await client.post(url, data=payload, headers=headers, timeout=30)
                response.raise_for_status()

            logger.info(f"Guest {guest_uid} successfully liked {target_uid} - Status: {response.status_code}")

            # Mark as used
            mark_used(target_uid, guest_uid, now_ms)
            return True, ""

        except httpx.HTTPStatusError as err:
            error_body = err.response.text if err.response else ""
            logger.warning(f"Guest {guest_uid} HTTP error: {err} - {error_body}")
            return False, f"http_error_{err.response.status_code if err.response else 'unknown'}"

        except httpx.RequestError as err:
            logger.warning(f"Guest {guest_uid} request error: {err}")
            return False, "request_error"

        except Exception as e:
            logger.error(f"Guest {guest_uid} unexpected error: {e}", exc_info=True)
            return False, f"error_{type(e).__name__}"


async def send_likes_with_guests(
    target_uid: str,
    amount: int,
    region: str = "IND"
) -> dict:
    """
    Send likes using guest accounts (free method)

    Args:
        target_uid: Target player's UID
        amount: Number of likes to send (up to available guests)
        region: Server region (IND, BR, US, etc.)

    Returns:
        {
            "success": bool,
            "likes_sent": int,
            "failed": int,
            "available_guests_remaining": int,
            "error": str (optional)
        }
    """
    # Load usage data
    async with _usage_lock:
        load_usage()

    # Check if guests file exists
    if not GUESTS_FILE.exists():
        logger.error(f"Guest file not found: {GUESTS_FILE}")
        return {
            "success": False,
            "likes_sent": 0,
            "failed": 0,
            "available_guests_remaining": 0,
            "error": "Guest accounts file not found"
        }

    # Load guest accounts
    try:
        with open(GUESTS_FILE, "r") as f:
            all_guests = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load guest accounts: {e}")
        return {
            "success": False,
            "likes_sent": 0,
            "failed": 0,
            "available_guests_remaining": 0,
            "error": f"Failed to load guest accounts: {str(e)}"
        }

    # Filter available (unused) guests for this target
    ensure_target(target_uid)
    available_guests = [
        g for g in all_guests
        if not guest_used_for_target(target_uid, str(g["uid"]))
    ]

    if not available_guests:
        logger.warning(f"No available guests for target {target_uid}")
        return {
            "success": False,
            "likes_sent": 0,
            "failed": 0,
            "available_guests_remaining": 0,
            "error": "All guest accounts exhausted for this target"
        }

    # Determine how many likes to send
    likes_to_send = min(amount, len(available_guests))
    base_url = get_base_url(region)

    logger.info(f"Sending {likes_to_send} likes to {target_uid} using guest accounts")

    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    # Send likes concurrently
    tasks = [
        like_with_guest(guest, target_uid, base_url, semaphore)
        for guest in available_guests[:likes_to_send]
    ]

    results = await asyncio.gather(*tasks)

    # Save usage data
    await save_usage()

    # Count successes and failures
    success_count = sum(1 for success, _ in results if success)
    failed_count = likes_to_send - success_count
    remaining_guests = len(available_guests) - likes_to_send

    logger.info(
        f"Guest likes complete for {target_uid}: "
        f"Success={success_count}, Failed={failed_count}, Remaining={remaining_guests}"
    )

    return {
        "success": success_count > 0,
        "likes_sent": success_count,
        "failed": failed_count,
        "available_guests_remaining": remaining_guests
    }


async def validate_guest_account(guest: dict) -> bool:
    """
    Validate if guest account is still working (not banned)

    Returns:
        bool: True if account is valid, False if banned/invalid
    """
    guest_uid = guest["uid"]
    guest_pass = guest["password"]

    try:
        # Try to get JWT token - this will fail if account is banned
        jwt_token, region, server_url = await create_jwt(guest_uid, guest_pass)

        if jwt_token and jwt_token != "0":
            logger.debug(f"Guest {guest_uid} validated successfully")
            return True
        else:
            logger.warning(f"Guest {guest_uid} validation failed - invalid credentials")
            return False

    except Exception as e:
        logger.error(f"Guest {guest_uid} validation error: {e}")
        return False


async def validate_all_guests() -> dict:
    """
    Validate all guest accounts and report status

    Returns:
        dict: {
            "total": int,
            "valid": int,
            "invalid": int,
            "invalid_uids": list
        }
    """
    logger.info("Starting guest account validation...")

    with open(GUESTS_FILE, "r") as f:
        all_guests = json.load(f)

    total = len(all_guests)
    valid = 0
    invalid_uids = []

    # Validate with concurrency limit
    semaphore = asyncio.Semaphore(10)  # 10 concurrent validations

    async def validate_with_semaphore(guest):
        async with semaphore:
            is_valid = await validate_guest_account(guest)
            if is_valid:
                return (guest["uid"], True)
            else:
                return (guest["uid"], False)

    tasks = [validate_with_semaphore(guest) for guest in all_guests]
    results = await asyncio.gather(*tasks)

    for uid, is_valid in results:
        if is_valid:
            valid += 1
        else:
            invalid_uids.append(uid)

    invalid = len(invalid_uids)

    logger.info(f"Guest validation complete: {valid}/{total} valid, {invalid} invalid")

    return {
        "total": total,
        "valid": valid,
        "invalid": invalid,
        "invalid_uids": invalid_uids
    }


async def remove_invalid_guests(invalid_uids: list):
    """
    Remove invalid guest accounts from the pool

    Args:
        invalid_uids: List of UIDs to remove
    """
    if not invalid_uids:
        logger.info("No invalid guests to remove")
        return

    logger.info(f"Removing {len(invalid_uids)} invalid guests from pool...")

    # Load current guests
    with open(GUESTS_FILE, "r") as f:
        all_guests = json.load(f)

    # Filter out invalid guests
    original_count = len(all_guests)
    valid_guests = [g for g in all_guests if g["uid"] not in invalid_uids]

    # Backup original file
    backup_file = GUESTS_FILE.with_suffix('.backup.json')
    with open(backup_file, "w") as f:
        json.dump(all_guests, f, indent=2)

    # Save filtered guests
    with open(GUESTS_FILE, "w") as f:
        json.dump(valid_guests, f, indent=2)

    removed_count = original_count - len(valid_guests)
    logger.info(f"Removed {removed_count} invalid guests. Backup saved to {backup_file}")


# Initialize on module load
load_usage()
