# Guest Account Creator Tool

This tool creates fresh Free Fire guest accounts to replace expired/blocked accounts.

## Why You Need This

Your current 166 accounts in `freefire/accounts.json` cannot authenticate with Garena anymore because:
- Garena detected and blocked bulk guest account usage
- Accounts may be expired or banned
- Anti-bot measures triggered

## How to Use

### Step 1: Run the Script

From the repository root:

```bash
cd tools
python3 create_guest_accounts.py
```

### Step 2: Answer the Prompts

```
📝 How many accounts to create? (recommended: 100-200): 150
⏱️  Delay between accounts in seconds? (recommended: 2-5): 3
```

**Important:**
- **Delay:** Use 2-5 seconds to avoid triggering Garena's anti-bot detection
- **Count:** 100-200 accounts is ideal (more = longer process)

### Step 3: Wait for Completion

The script will:
1. Create accounts one by one with delays
2. Show progress in real-time
3. Save to `freefire/accounts.json` automatically

Example output:
```
🚀 Creating 100 guest accounts...
⏱️  Delay between accounts: 3s
📊 Progress:

✅ 1/100 - UID: 1234567890
✅ 2/100 - UID: 1234567891
✅ 3/100 - UID: 1234567892
...

📊 Summary:
   ✅ Successful: 95
   ❌ Failed: 5
   📈 Success Rate: 95.0%

💾 Saved 95 accounts to ../freefire/accounts.json
```

### Step 4: Deploy to Railway

After accounts are created:

```bash
git add freefire/accounts.json
git commit -m "Update guest accounts with fresh credentials"
git push origin main
```

Railway will auto-deploy with the new accounts.

### Step 5: Test

After deployment:
```
/likes 809563592
```

Should now work with the fresh accounts!

## Troubleshooting

### "All accounts failed to create"

**Cause:** Garena API is blocking account creation from your IP

**Solutions:**
1. Try from a different network/IP
2. Use a VPN
3. Increase delay to 5-10 seconds
4. Create smaller batches (20-30 at a time)

### "Success rate < 50%"

**Cause:** Rate limiting kicking in

**Solutions:**
1. Increase delay between accounts
2. Create accounts in smaller batches
3. Wait 1 hour between batches

### "Accounts work initially but fail later"

**Cause:** Garena detecting patterns and banning accounts

**Solutions:**
1. This is why Option 1 (HL Gaming Premium API) is better long-term
2. Accounts may need frequent refreshing
3. Consider using the Premium API instead

## Alternative: HL Gaming Premium API

If you keep having issues with guest accounts, I recommend using HL Gaming Premium API:

- ✅ No guest account issues
- ✅ Instant delivery (< 5 seconds)
- ✅ 100% reliable
- ✅ No rate limiting
- ✅ Official service

See `HL_GAMING_SETUP.md` for setup instructions.

## Support

If guest account creation fails repeatedly, the issue is likely:
1. Garena's anti-bot measures blocking creation
2. Your IP being rate limited

In this case, **HL Gaming Premium API is the only reliable solution**.
