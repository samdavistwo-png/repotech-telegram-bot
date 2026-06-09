# Guest Accounts Directory

## Security Warning

This directory contains guest account credentials. DO NOT:
- Commit `guests_converted.json` to git
- Share this file publicly
- Include in backups sent to third parties

## Files

- `guests_converted.json` - Active guest accounts (PRIVATE - Protected by .gitignore)
- `formatted_guests.json` - Human-readable format (PRIVATE - Protected by .gitignore)
- `guests_converted.backup.json` - Automatic backup before removal (PRIVATE - Protected by .gitignore)
- `count_guest.py` - Utility script (safe to commit)
- `README.md` - This file (safe to commit)

## Guest Account Management

### Validation Commands (Admin Only)

Check which guest accounts are still working:
```
/validguests
```

Remove invalid/banned guest accounts:
```
/removeinvalid
```

### How It Works

1. Guest accounts are validated by attempting to get a JWT token
2. Accounts that fail authentication are marked as invalid
3. Invalid accounts can be safely removed with automatic backup
4. Backup file (`guests_converted.backup.json`) is created before any removals

### Security Best Practices

1. Never commit credential files to version control
2. Keep backups in a secure, encrypted location
3. Regularly validate guest accounts to maintain quality
4. Monitor usage logs for suspicious activity

## Automated Protection

The `.gitignore` file automatically prevents credential files from being committed:
```
freefire/guests_manager/guests_converted.json
freefire/guests_manager/guests_converted.backup.json
freefire/guests_manager/formatted_guests.json
usage_history/
```

## Support

For issues with guest account management, contact the system administrator.
