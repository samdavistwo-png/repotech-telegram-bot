

# Sambots Likes System - Complete Documentation

## Overview

The Sambots system creates 100+ Free Fire MAX guest accounts named `Sambots##1##`, `Sambots##2##`, etc., and uses them to send 100% real likes in batches of 30 accounts with logout/login cycles.

## System Components

### 1. Bulk Account Creator
**File:** `freefire/ffmax_bulk_creator.py`

Creates bulk guest accounts with custom naming:
- ✅ Creates 100+ accounts automatically
- ✅ Names each account: Sambots##1##, Sambots##2##, etc.
- ✅ Supports both Free Fire and Free Fire MAX
- ✅ Sets in-game nicknames
- ✅ Saves to `freefire/sambots_accounts.json`

**Usage:**
```bash
cd freefire
python3 ffmax_bulk_creator.py

# Select:
# 1. Free Fire MAX (India Server) - RECOMMENDED
# 2. Free Fire Regular (India Server)

# Enter:
# - Number of accounts: 100-150
# - Delay: 3-5 seconds
```

**Output:**
```json
{
  "accounts": [
    {
      "uid": "1234567890",
      "password": "abc123def",
      "name": "Sambots##1##",
      "nickname_set": true,
      "type": "ffmax"
    },
    ...
  ],
  "created_at": "2024-01-01T12:00:00",
  "total_accounts": 100
}
```

### 2. Batch Processing Engine
**File:** `freefire/batch_likes_engine.py`

Processes likes in batches with logout/login cycles:
- ✅ Processes 30 accounts per batch (configurable)
- ✅ Automatic login for each account
- ✅ Sends like with AES-CBC encryption
- ✅ Automatic logout after batch completes
- ✅ Tracks success/failure per batch
- ✅ Overall statistics reporting

**Key Functions:**
```python
# Load Sambots accounts
accounts = load_sambots_accounts()

# Send 100 likes using batch system
result = await send_likes_all_batches(
    accounts=accounts,
    target_uid="1234567890",
    total_likes=100
)

# Result contains:
{
    "total_attempted": 100,
    "total_successful": 98,
    "total_failed": 2,
    "success_rate": 98.0,
    "batches": [...]
}
```

### 3. Player Info Fetcher
**File:** `freefire/ffmax_player_api.py`

Fetches REAL player names from multiple sources:
- ✅ Method 1: FF MAX Garena antispam API
- ✅ Method 2: FF MAX profile API
- ✅ Method 3: Regular FF Garena antispam API
- ✅ Method 4: Regular FF profile API
- ✅ Method 5: Third-party alternative APIs

**Usage:**
```python
from freefire.ffmax_player_api import get_complete_player_info

player_info = await get_complete_player_info("1234567890")

# Returns:
{
    "success": True,
    "name": "ProGamer123",
    "likes": 5000,
    "level": 65,
    "game": "FF MAX"
}
```

### 4. Telegram Handler
**File:** `handlers/likes_sambots.py`

Complete bot integration:
- ✅ Fetches real player name and info
- ✅ Shows before/after likes count
- ✅ Displays success rate
- ✅ Automatic balance management
- ✅ Error handling with refunds
- ✅ Detailed progress messages

## Setup Instructions

### Step 1: Create Sambots Accounts

```bash
cd /workspace/claude-workspace/samdavistwo_gmail.com/samdavistwo-png/repotech-telegram-bot/freefire

python3 ffmax_bulk_creator.py
```

**Recommended Settings:**
- Accounts: 100-150
- Delay: 3-5 seconds
- Game: Free Fire MAX (option 1)

**Expected Output:**
```
============================================================
FREE FIRE MAX GUEST ACCOUNT CREATOR
============================================================
⏱️  Delay: 3.0s between accounts
🎮 Game: Free Fire MAX
📝 Naming: Sambots##1## to Sambots##100##

📊 Progress:

[1/100] Creating Sambots##1##... ✅ SUCCESS + Nickname Set
[2/100] Creating Sambots##2##... ✅ SUCCESS + Nickname Set
...
[100/100] Creating Sambots##100##... ✅ SUCCESS

============================================================
📊 SUMMARY:
   ✅ Successful: 98/100
   ❌ Failed: 2/100
   📈 Success Rate: 98.0%
============================================================

💾 Saved 98 accounts to ../freefire/sambots_accounts.json
```

### Step 2: Update Bot Handler

Replace the current likes handler with Sambots handler:

**In `bot.py`:**
```python
# Replace this:
# from handlers.likes_superfast import likes_handler

# With this:
from handlers.likes_sambots import likes_sambots_handler

# Update the handler registration:
application.add_handler(CommandHandler("likes", likes_sambots_handler))
```

### Step 3: Deploy to Railway

```bash
git add freefire/sambots_accounts.json
git add handlers/likes_sambots.py
git add freefire/batch_likes_engine.py
git add freefire/ffmax_player_api.py
git add freefire/ffmax_bulk_creator.py

git commit -m "ADD: Sambots bulk likes system with batch processing"
git push origin main
```

Railway will automatically deploy within 3-5 minutes.

### Step 4: Test

```bash
/likes 1234567890
```

**Expected Response:**
```
✅ Player Found!

👤 Name: ProGamer123
📊 Level: 65
🎮 Game: FF MAX
❤️  Current Likes: 5,000

🚀 Processing 100 likes...
⏳ Using Sambots batch system (30 accounts per batch)...

✅ Likes sent successfully!

👤 Player: ProGamer123
📊 Level: 65
🎮 Game: FF MAX

❤️  Likes Before: 5,000
➕ Likes Added: 98
❤️  Likes After: 5,098

📊 Success Rate: 98.0%
✅ Successful: 98/100
❌ Failed: 2/100

💰 Coins deducted: 50
```

## How It Works

### Batch Processing Flow

```
User sends: /likes 1234567890
    ↓
1. Fetch player info (FF MAX + FF APIs)
    ↓
2. Verify balance (50 coins required)
    ↓
3. Load Sambots accounts (100+ accounts)
    ↓
4. Deduct coins
    ↓
5. Split accounts into batches of 30
    ↓
6. For each batch:
   - Login 30 accounts (get JWT tokens)
   - Send 30 likes concurrently
   - Logout (JWT expires automatically)
   - Small delay (2 seconds)
    ↓
7. Calculate total success/failure
    ↓
8. Show final results
    ↓
9. If all failed → refund coins
```

### Batch System Advantages

1. **Avoids Rate Limiting:** Only 30 concurrent requests at a time
2. **Natural Logout:** JWT tokens expire after each batch
3. **Progressive Delivery:** Users see likes adding in waves
4. **Error Isolation:** One batch failure doesn't affect others
5. **Garena-Friendly:** Mimics human-like usage patterns

## Configuration

### Batch Size

**File:** `freefire/batch_likes_engine.py`

```python
BATCH_SIZE = 30  # Change to 20-50 as needed
```

- **Lower (20):** Slower but more reliable
- **Higher (50):** Faster but may trigger rate limits

### Concurrent Requests

```python
semaphore = asyncio.Semaphore(10)  # Max 10 concurrent per batch
```

- **Lower (5):** Very safe, slower
- **Higher (15):** Faster, slight risk

### Delays Between Batches

```python
await asyncio.sleep(2)  # 2 seconds between batches
```

- **Increase to 5:** If getting rate limited
- **Decrease to 1:** If very reliable

## Troubleshooting

### Issue: UID Not Found (HTTP 404)

**Symptom:**
```
❌ Could not verify player UID: 1810201201
This UID may not exist or APIs are temporarily down.
```

**Causes:**
- UID does not exist in Free Fire/FF MAX
- Player has strict privacy settings
- Wrong server region (IND vs SG)

**Solution:**
- Verify UID is correct
- Try a different known-working UID
- Check if player is on India server

### Issue: All Sambots Failed Authentication

**Symptom:**
```
❌ All 100 Sambots accounts failed to send likes.
```

**Causes:**
- Sambots accounts expired/banned by Garena
- Garena blocking bulk guest authentication
- Wrong server URL (FF vs FF MAX)

**Solution:**
```bash
# Create fresh Sambots accounts
cd freefire
python3 ffmax_bulk_creator.py

# Select Free Fire MAX
# Create 100-150 new accounts
```

### Issue: Low Success Rate (< 50%)

**Symptom:**
```
📊 Success Rate: 35.0%
✅ Successful: 35/100
❌ Failed: 65/100
```

**Causes:**
- Some Sambots accounts are invalid
- Network issues
- Garena API rate limiting

**Solutions:**
1. **Increase delays:**
   ```python
   BATCH_SIZE = 20  # Reduce batch size
   await asyncio.sleep(5)  # Increase delay
   ```

2. **Create more accounts:**
   - Create 150-200 accounts instead of 100
   - System will use first 100 working accounts

3. **Filter accounts:**
   ```bash
   # Test each account and remove non-working ones
   python3 test_sambots_accounts.py
   ```

### Issue: Not Enough Sambots Accounts

**Symptom:**
```
⚠️ Not enough Sambots accounts!
Available: 50 accounts
Required: 100 accounts
```

**Solution:**
```bash
cd freefire
python3 ffmax_bulk_creator.py

# Create additional 50-100 accounts
# They will be added to existing accounts
```

## Monitoring

### Check Logs

```bash
# On Railway
railway logs

# Look for:
📦 Batch 1/4: Processing 30 accounts...
📦 Batch 1/4 Complete: ✅ 28 | ❌ 2
📦 Batch 2/4: Processing 30 accounts...
📦 Batch 2/4 Complete: ✅ 30 | ❌ 0
...
✅ All batches complete!
   📊 Total Successful: 98/100
```

### Success Metrics

- **95-100% success rate:** Excellent
- **80-95% success rate:** Good (normal)
- **60-80% success rate:** Fair (consider refreshing accounts)
- **< 60% success rate:** Poor (create fresh accounts)

## Alternative: HL Gaming Premium API

If Sambots system continues to have issues with Garena's anti-bot measures, use HL Gaming Premium API instead:

**Advantages:**
- ✅ 100% success rate
- ✅ Instant delivery (< 5 seconds)
- ✅ No account management needed
- ✅ Bypasses all Garena restrictions

**Setup:**
1. Visit: https://www.hlgamingofficial.com/p/api.html
2. Get API credentials
3. Add to Railway environment variables:
   ```
   HL_GAMING_USERUID=your_uid
   HL_GAMING_API_KEY=your_key
   ```

## Support

If you encounter issues:
1. Check Railway logs for error details
2. Test with known-working UID: `809563592`
3. Verify Sambots accounts file exists: `freefire/sambots_accounts.json`
4. Try creating fresh accounts
5. Consider HL Gaming Premium API as alternative
