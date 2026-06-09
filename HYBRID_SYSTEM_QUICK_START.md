# Hybrid Likes System - Quick Start Guide

## What Changed?

The `/likes` command now uses a **Hybrid System**:
1. **Try guest accounts first** (FREE - 161 available per target)
2. **Fallback to HL Gaming** if guests exhausted or failed

## User Experience

### No Changes for Users
- Same command: `/likes <uid>`
- Same price: 50 coins for 100 likes
- Same speed: < 10 seconds

### What's Better
- First ~161 likes per target are FREE (saves API costs)
- Automatic fallback (no failures)
- Shows which method was used
- Shows remaining guests

## How It Works

```
User: /likes 1234567890

Bot: 🔍 Fetching player info...
     🎁 Available guests: 161

Bot: ✅ Player Found!
     👤 Name: PlayerXYZ
     ❤️ Current Likes: 1,234
     🚀 Sending 100 likes...
     🎁 Trying Guest Accounts...

Bot: ✅ Likes sent successfully!
     ❤️ Likes Before: 1,234
     ➕ Likes Added: 100
     ❤️ Likes After: 1,334

     🎁 Method: Guest Accounts (Free)
     🔢 Remaining Guests: 61 for this player

     💰 Coins deducted: 50
```

## Files to Know

### Guest Accounts
**Location**: `freefire/guests_manager/guests_converted.json`
**Count**: 161 accounts
**Format**:
```json
[
  {"uid": "4103677597", "password": "BE281AB..."},
  {"uid": "4103730521", "password": "4182D9..."}
]
```

### Usage Tracking
**Location**: `usage_history/guest_usage_by_target.json`
**Auto-created**: Yes (on first /likes command)
**Format**:
```json
{
  "1234567890": {
    "used_guests": {
      "4103677597": 1717927284000
    },
    "total_likes": 1
  }
}
```

### Main Code
- `freefire/guest_likes_engine.py` - Guest management
- `handlers/likes_hybrid.py` - Hybrid handler
- `freefire/get_jwt.py` - Auth (FIXED: was using localhost)

## Monitoring

### Check Logs
Look for these messages:

**Guest Success**:
```
INFO - Guest 4103677597 successfully liked 1234567890
INFO - Guest likes complete: Success=100, Failed=0
```

**Fallback to HL Gaming**:
```
WARNING - Guest method PARTIAL/FAILED. Falling back to HL Gaming...
INFO - HL Gaming fallback SUCCESS
```

### Check Usage File
```bash
cat usage_history/guest_usage_by_target.json
```
Shows which guests have been used for which targets.

### Check Guest Count
```bash
python3 -c "import json; print(len(json.load(open('freefire/guests_manager/guests_converted.json'))))"
# Output: 161
```

## Troubleshooting

### Problem: "All guest accounts exhausted"
**Normal Behavior**: Each guest can only like a target once
**What Happens**: System uses HL Gaming automatically
**User Impact**: None (still gets 100 likes)

### Problem: "Guest method error"
**Cause**: Network issue, JWT failure, etc.
**What Happens**: System uses HL Gaming automatically
**User Impact**: None (still gets 100 likes)

### Problem: Both methods fail
**What Happens**: User gets error + full refund
**Action**: Check HL Gaming API credentials

### Problem: Usage file corrupted
**Solution**:
```bash
rm usage_history/guest_usage_by_target.json
# Will recreate on next /likes command
```

## Cost Savings Example

### Before (Only HL Gaming)
- Every /likes = HL Gaming API credit used
- 1000 requests = 1000 API credits

### After (Hybrid System)
- First 161 likes/target = FREE (guests)
- After that = HL Gaming API credit

**Example with 10 different targets**:
- Requests: 10 × 100 likes = 1000 likes total
- Guest used: 1000 likes (all FREE)
- HL Gaming used: 0 credits
- **Savings**: 100%

**Example with same target 200 times**:
- Requests: 200 × 100 likes = 20,000 likes total
- Guest used: 161 × 100 = 16,100 likes (FREE)
- HL Gaming used: 39 × 100 = 3,900 likes (API credits)
- **Savings**: 80.5%

## Validation

Run this to verify everything:
```bash
./validate_hybrid_implementation.sh
```

Expected output:
```
✅ PASS - get_jwt.py uses correct URL
✅ PASS - guest_likes_engine.py created
✅ PASS - likes_hybrid.py created
✅ PASS - Hybrid handler registered
...
🎉 ALL VALIDATIONS PASSED!
```

## Quick Commands

```bash
# Check if system is active
grep -n "likes_hybrid_handler" bot.py

# Count total guests
python3 -c "import json; print(len(json.load(open('freefire/guests_manager/guests_converted.json'))))"

# View usage for specific target
python3 -c "import json; data=json.load(open('usage_history/guest_usage_by_target.json')); print(json.dumps(data.get('YOUR_UID', {}), indent=2))"

# Reset usage for testing (CAUTION)
rm usage_history/guest_usage_by_target.json
```

## What to Tell Users

**Message Template**:
```
🎉 System Upgrade!

The /likes command now uses a smart hybrid system:
- Tries FREE guest accounts first
- Falls back to premium API if needed
- Same price, same speed, better reliability!

No action needed - just use /likes as normal!
```

## Environment Variables

**No changes required!** Uses existing:
- `HL_GAMING_USERUID` - Already set
- `HL_GAMING_API_KEY` - Already set

## Rollback (If Needed)

If you need to revert to HL Gaming only:

1. Edit `bot.py` line 53:
   ```python
   from handlers.likes_hl_gaming import likes_hl_gaming_handler
   ```

2. Edit `bot.py` line 144:
   ```python
   application.add_handler(CommandHandler("likes", likes_hl_gaming_handler))
   ```

3. Restart bot

## Support

**Files to check**:
1. Bot logs (console output)
2. `usage_history/guest_usage_by_target.json`
3. `freefire/guests_manager/guests_converted.json`

**Common Issues**:
- ✅ Guests exhausted → Normal, uses HL Gaming
- ✅ JWT errors → Retries with next guest
- ✅ Both methods fail → Refunds user

**Success Indicators**:
- Users getting likes successfully
- `usage_history/` directory exists
- Guest usage JSON file growing
- Logs showing "guest" method

---

**Status**: ✅ Production Ready
**Validation**: All tests passed
**Impact**: Zero (seamless upgrade)
