# 🚨 AFROTC 695 Data Recovery System

**Use this when Cursor/AI breaks your data!**

## Quick Fix (One Command)

When your data gets corrupted or deleted:

```bash
python FIX_DATA.py
```

This will automatically:
- Find the most recent backup
- Restore all your data
- Show you what was restored

## Full Recovery System

For more control, use the interactive system:

```bash
python data_recovery_system.py
```

This gives you options to:
1. Check current database state
2. List available backups
3. Recover from most recent backup
4. Recover from specific backup
5. Create emergency backup

## What Gets Restored

The recovery system restores:
- ✅ Cadets (19 records)
- ✅ University Contacts (13 records)
- ✅ Potential Recruits
- ✅ Recruitment Events (2 records)
- ✅ External Links (5 records)
- ✅ Recruitment Documents (6 records)
- ✅ Activity Logs
- ✅ Password History

## Backup Files

Your backups are stored in the `backups/` directory:
- `afrotc695_backup_20250817_005043.json` - Most recent (61 records)
- `afrotc695_backup_20250816_233212.json` - Previous (54 records)
- `neon_backup_20250807_145537.json` - Older (16 records)

## When to Use

Use the recovery system when:
- ❌ Cursor/AI code breaks your database
- ❌ Data gets corrupted
- ❌ Tables are empty unexpectedly
- ❌ You see "DATA LOSS DETECTED" messages

## Prevention

To prevent data loss:
1. Always backup before major changes
2. Test code changes on a copy first
3. Use the emergency backup feature before risky operations

## Emergency Backup

Create a backup of current state:
```bash
python data_recovery_system.py
# Choose option 5: Create emergency backup
```

---

**Remember: When in doubt, run `python FIX_DATA.py`!**
