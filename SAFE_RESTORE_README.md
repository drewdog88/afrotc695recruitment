# Safe Restore System

A simple, safe database restoration system for AFROTC 695.

## How to Use

### 1. Run the restore script
```bash
python safe_restore.py
```

### 2. What happens:
1. **Lists available backups** from R2 storage
2. **Shows backup details** (date, size, description)
3. **Lets you select** which backup to restore
4. **Shows what will be restored** (tables and record counts)
5. **Asks for confirmation** (type 'RESTORE' to continue)
6. **Creates a safety backup** before proceeding
7. **Restores the data** from your selected backup

### 3. Safety Features:
- ✅ **Safety backup created** before any changes
- ✅ **Clear confirmation** required
- ✅ **Shows exactly what will be restored**
- ✅ **Rollback capability** (use safety backup if needed)

## Example Output

```
🔄 AFROTC 695 Safe Restore System
==================================================
📂 Available Backups:
1. afrotc695_backup_daily_20250110_143022.json
   📅 2025-01-10 14:30:22 | 📦 24567 bytes
2. afrotc695_backup_daily_20250110_020000.json
   📅 2025-01-10 02:00:00 | 📦 23456 bytes

Select backup (1-2): 1

📥 Downloading afrotc695_backup_daily_20250110_143022.json...

🚨 RESTORE CONFIRMATION
==================================================
Backup: Nightly automatic backup
Created: 2025-01-10T14:30:22
Type: daily
Total records: 1250

Tables to restore:
  - user: 15 records
  - potential_recruit: 450 records
  - cadet: 85 records
  - university_contact: 25 records
  - recruitment_event: 45 records
  - external_link: 12 records
  - recruitment_document: 8 records
  - activity_log: 610 records

⚠️  This will overwrite current data!
Type 'RESTORE' to continue: RESTORE

📸 Creating safety backup...
✅ Safety backup created: afrotc695_backup_emergency_20250110_150000.json

🔄 Executing restore...
🔄 Restoring user: 15 records
   ✅ Restored 15/15 records
🔄 Restoring potential_recruit: 450 records
   ✅ Restored 450/450 records
...

✅ Restore completed! 1250 records restored
📸 Safety backup: afrotc695_backup_emergency_20250110_150000.json
```

## Future Web Interface

This script is designed to be easily adapted for web use:
- Functions are modular and reusable
- Clear separation of concerns
- Easy to add web endpoints
- Safety features can be applied to web interface

## Requirements

- Python 3.7+
- `psycopg2` for database connection
- `boto3` for R2 storage access
- Environment variables:
  - `DATABASE_URL`
  - `CLOUDFLARE_R2_ACCOUNT_ID`
  - `CLOUDFLARE_R2_ACCESS_KEY_ID`
  - `CLOUDFLARE_R2_SECRET_ACCESS_KEY`
