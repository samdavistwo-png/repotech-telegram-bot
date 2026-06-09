# Guest Account Creation & Management Guide

## Overview
This guide explains how to create and manage Free Fire guest accounts for the likes system.

## Current Status
- **Guest Accounts**: 161 accounts available
- **Location**: `freefire/guests_manager/guests_converted.json`
- **Format**: `[{"uid": "...", "password": "..."}]`

## Account Creation Methods

### Method 1: Simple Bulk Creator (Recommended)
Uses urllib only, no external dependencies needed.

```bash
python create_guests_simple.py
```

**Features**:
- Creates 100 accounts with one command
- Uses Free Fire guest registration API
- 3 second delay between accounts (rate limiting)
- Automatic backup of existing accounts
- Progress tracking

**Output**:
- `freefire/guests_manager/new_guests_2026.json` - New accounts
- `freefire/guests_manager/guests_converted.json` - Updated main file
- `freefire/guests_manager/guests_converted.backup.json` - Backup

### Method 2: Advanced Bulk Creator (Multiple Methods)
Uses multiple account creation methods for redundancy.

```bash
python create_bulk_guests.py
```

**Requires**:
- httpx
- pycryptodome
- protobuf

**Features**:
- Method 1: temp_account_creator (50 accounts, async)
- Method 2: ffmax_bulk_creator (30 accounts, sync)
- Method 3: working_bulk_system (20 accounts, signed)
- Total: 100 accounts with redundancy

### Method 3: Manual Creation
Create accounts one at a time for testing.

```python
from freefire.ffmax_bulk_creator import create_guest_account

result = create_guest_account(account_number=1, use_ffmax=False)
if result.get("success"):
    print(f"UID: {result['uid']}")
    print(f"Password: {result['password']}")
```

## Account Validation

### Validate All Accounts
```bash
python validate_new_accounts.py
```

**Checks**:
1. OAuth token generation (Garena API)
2. JWT token generation (with fallback)
3. Overall readiness for use

**Output**:
```
📊 VALIDATION RESULTS:
   Total Accounts: 161
   OAuth Valid: 158/161 (98.1%)
   JWT Valid: 158/161 (98.1%)
   Ready to Use: 158/161 (98.1%)
```

### Validate Sample Account
```bash
python validate_new_accounts.py --sample
```

Tests just one account for quick verification.

### Test JWT Fallback
```bash
python test_jwt_fallback.py
```

Tests the JWT authentication fallback system.

### Test Multiple Accounts
```bash
python test_jwt_fallback.py --multi 10
```

Tests JWT generation for 10 accounts.

## Account File Format

### guests_converted.json
```json
[
  {
    "uid": "4103677597",
    "password": "BE281AB62B3F3A7FE98CE28881C0D55F6256151257D10DC068686FBF462CEF9C"
  },
  {
    "uid": "4103730521",
    "password": "4182D9E3ECDEDC503C159AD940D230A8224BBB288C8DE03417AE28A985F056E5"
  }
]
```

**Fields**:
- `uid`: Free Fire account UID (numeric string)
- `password`: Hex-encoded password from Garena API

## Account Management

### Check Account Count
```python
import json
from pathlib import Path

with open('freefire/guests_manager/guests_converted.json') as f:
    accounts = json.load(f)
print(f"Total accounts: {len(accounts)}")
```

### Remove Invalid Accounts
```python
from freefire.guest_likes_engine import validate_all_guests, remove_invalid_guests
import asyncio

# Validate all accounts
result = asyncio.run(validate_all_guests())

# Remove invalid ones
asyncio.run(remove_invalid_guests(result['invalid_uids']))
```

### Merge Account Files
```python
import json

# Load multiple account files
with open('file1.json') as f:
    accounts1 = json.load(f)
with open('file2.json') as f:
    accounts2 = json.load(f)

# Merge and remove duplicates
all_accounts = accounts1 + accounts2
unique_accounts = []
seen_uids = set()

for acc in all_accounts:
    if acc['uid'] not in seen_uids:
        unique_accounts.append(acc)
        seen_uids.add(acc['uid'])

# Save merged accounts
with open('merged_accounts.json', 'w') as f:
    json.dump(unique_accounts, f, indent=2)

print(f"Merged {len(unique_accounts)} unique accounts")
```

## Account Usage Tracking

### Check Available Guests for Target
```python
from freefire.guest_likes_engine import get_available_guests

target_uid = "1810201201"
available = get_available_guests(target_uid)
print(f"Available guests for {target_uid}: {available}")
```

### View Usage History
```python
import json

with open('usage_history/guest_usage_by_target.json') as f:
    usage = json.load(f)

for target_uid, data in usage.items():
    print(f"Target {target_uid}: {data['total_likes']} likes sent")
    print(f"  Used guests: {len(data['used_guests'])}")
```

### Reset Usage for Target (Dangerous!)
```python
import json

with open('usage_history/guest_usage_by_target.json') as f:
    usage = json.load(f)

# Remove specific target
target_uid = "1810201201"
if target_uid in usage:
    del usage[target_uid]

# Save
with open('usage_history/guest_usage_by_target.json', 'w') as f:
    json.dump(usage, f, indent=2)
```

## Troubleshooting

### Problem: Account creation fails with "Bad Request"

**Cause**: Garena API rejecting requests
**Solution**:
1. Increase delay between creations (3-5 seconds)
2. Try different times of day
3. Use VPN if IP is rate-limited
4. Check if API endpoint changed

### Problem: Account creation fails with "Name or service not known"

**Cause**: Network issue or DNS failure
**Solution**:
1. Check internet connection
2. Try different DNS servers
3. Check if Garena servers are down
4. Use alternative creation method

### Problem: Accounts created but validation fails

**Cause**: Accounts might be banned or invalid
**Solution**:
```bash
python validate_new_accounts.py
```

This will show which accounts are invalid and why.

### Problem: "No module named 'httpx'"

**Cause**: Missing dependencies
**Solution**:
```bash
pip install httpx pycryptodome protobuf
```

Or use the simple creator which doesn't need external deps:
```bash
python create_guests_simple.py
```

## Best Practices

### 1. Rate Limiting
- Use 3-5 second delay between account creations
- Don't create more than 100 accounts per hour
- Space out creation over multiple days

### 2. Backup Strategy
- Always backup before creating new accounts
- Keep multiple backup copies
- Test new accounts before deploying

### 3. Account Rotation
- Use different accounts for different targets
- Track usage to avoid exhausting accounts
- Create new accounts periodically

### 4. Validation Schedule
- Validate accounts weekly
- Remove invalid accounts immediately
- Monitor success rates

### 5. Security
- Never commit passwords to git (use .gitignore)
- Encrypt account files if storing remotely
- Rotate accounts if compromised

## Scripts Reference

| Script | Purpose | Dependencies |
|--------|---------|--------------|
| `create_guests_simple.py` | Create 100 accounts | None (uses urllib) |
| `create_bulk_guests.py` | Create 100 accounts (multi-method) | httpx, pycryptodome, protobuf |
| `validate_new_accounts.py` | Validate all accounts | httpx, protobuf |
| `test_jwt_fallback.py` | Test JWT authentication | httpx, protobuf |

## Files Structure

```
freefire/guests_manager/
├── guests_converted.json           # Main account file (161 accounts)
├── guests_converted.backup.json    # Backup before changes
├── new_guests_2026.json           # Newly created accounts
├── formatted_guests.json          # Alternative format
├── README.md                      # Guest manager docs
├── count_guest.py                 # Count accounts script
├── rm_duplicates.py               # Remove duplicate accounts
└── save_guest.py                  # Save account script

usage_history/
└── guest_usage_by_target.json     # Track which accounts used for which targets
```

## Quick Start

### Create New Accounts
```bash
# Simple method (no dependencies)
python create_guests_simple.py

# Advanced method (multiple methods)
python create_bulk_guests.py
```

### Validate Accounts
```bash
# Validate all
python validate_new_accounts.py

# Quick test
python validate_new_accounts.py --sample
```

### Test JWT System
```bash
# Test one account
python test_jwt_fallback.py

# Test multiple
python test_jwt_fallback.py --multi 10
```

## Next Steps

1. **Deploy to Production**: The accounts are ready for use
2. **Monitor Usage**: Track which accounts are being used
3. **Periodic Validation**: Run validation weekly
4. **Create More Accounts**: When current pool is exhausted

## Support

For issues:
1. Check `JWT_FALLBACK_SOLUTION.md` for authentication issues
2. Run `validate_new_accounts.py` to diagnose problems
3. Check Garena API status
4. Review error logs in bot output
