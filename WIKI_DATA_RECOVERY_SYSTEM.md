# AFROTC 695 Data Recovery System Wiki

## Overview

The AFROTC 695 Data Recovery System is a comprehensive backup and restoration solution designed to protect against data loss caused by development errors, particularly those that may occur during AI-assisted coding sessions. This system was built in response to a critical data loss incident where the production database was corrupted due to problematic 2-factor authentication code.

## System Architecture

### Core Components

1. **`data_recovery_system.py`** - Main recovery class with full functionality
2. **`FIX_DATA.py`** - One-command emergency recovery script
3. **`DATA_RECOVERY_README.md`** - User-friendly usage guide
4. **Backup Storage** - JSON-based backup files in `backups/` directory
5. **Database Connection** - Direct PostgreSQL connection to Neon database

### Database Configuration

The system connects directly to the production PostgreSQL database hosted on Neon:

```python
DATABASE_URL = "postgresql://neondb_owner:npg_5qC7jUoluvOY@ep-crimson-hall-admf1mo5-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"
```

**Note**: This hardcoded connection string bypasses environment variable loading issues that were the root cause of the original production server failure.

## Data Recovery System Class (`data_recovery_system.py`)

### Class Structure

```python
class DataRecoverySystem:
    def __init__(self):
        self.backup_dir = Path("backups")
        self.conn = None
        self.cursor = None
```

### Key Methods

#### 1. Database Connection
```python
def connect_db(self):
    """Establish connection to production PostgreSQL database"""
```

**Purpose**: Creates a direct connection to the Neon database using psycopg2
**Error Handling**: Returns False if connection fails, prints detailed error message

#### 2. List Available Backups
```python
def list_backups(self):
    """List all available backup files with metadata"""
```

**Returns**: List of backup files sorted by creation date
**Metadata**: Includes timestamp, description, and record counts
**Filtering**: Automatically excludes metadata-only files

#### 3. Analyze Backup Contents
```python
def analyze_backup(self, backup_file):
    """Analyze the contents of a specific backup file"""
```

**Output**:
- Backup timestamp and description
- Record counts per table
- Total record count
- Data structure overview

#### 4. Restore from Backup
```python
def restore_from_backup(self, backup_file=None, tables=None):
    """Restore data from a backup file"""
```

**Parameters**:
- `backup_file`: Specific backup file path (defaults to most recent)
- `tables`: List of specific tables to restore (defaults to all main tables)

**Restoration Process**:
1. Loads JSON backup data
2. Clears existing data from target tables
3. Inserts backup data in proper order
4. Handles foreign key constraints
5. Reports success/failure for each table

#### 5. Create Emergency Backup
```python
def create_emergency_backup(self, description="Emergency backup"):
    """Create a backup of current database state"""
```

**Purpose**: Creates a snapshot before risky operations
**Format**: JSON file with timestamp and description
**Location**: `backups/` directory with timestamped filename

### Table Restoration Order

The system restores tables in a specific order to handle foreign key dependencies:

```python
main_tables = [
    'user',
    'cadet',
    'university_contact',
    'document',
    'activity_log'
]
```

**Strategy**: Restores core tables first, then dependent tables to avoid constraint violations.

## Emergency Recovery Script (`FIX_DATA.py`)

### Purpose
Provides a one-command solution for immediate data recovery when the database is corrupted.

### Usage
```bash
python FIX_DATA.py
```

### What It Does
1. **Automatic Detection**: Finds the most recent backup file
2. **Database Connection**: Connects directly to production database
3. **Data Restoration**: Restores all main tables from backup
4. **Progress Reporting**: Shows real-time restoration progress
5. **Error Handling**: Gracefully handles and reports any issues

### Output Example
```
🚨 FIXING YOUR DATA...
==================================================
✅ Found most recent backup: afrotc695_backup_20250817_005043.json
✅ Connected to production database
🔄 Restoring user table... 19 records restored
🔄 Restoring cadet table... 19 records restored
🔄 Restoring university_contact table... 13 records restored
🔄 Restoring document table... 10 records restored
✅ Data restoration complete! 61 total records restored
```

## Backup File Format

### JSON Structure
```json
{
  "timestamp": "2025-08-17T00:50:43",
  "description": "Automatic backup before 2FA implementation",
  "created_at": "2025-08-17T00:50:43",
  "tables": {
    "user": [
      {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "role": "admin",
        "created_at": "2025-08-16T10:30:00"
      }
    ],
    "cadet": [
      {
        "id": 1,
        "user_id": 2,
        "first_name": "John",
        "last_name": "Doe",
        "rank": "C/2d Lt"
      }
    ]
  }
}
```

### File Naming Convention
- Format: `afrotc695_backup_YYYYMMDD_HHMMSS.json`
- Example: `afrotc695_backup_20250817_005043.json`
- Metadata files: `*_metadata.json` (automatically filtered out)

## Usage Scenarios

### Scenario 1: Emergency Data Recovery
**When**: Database is corrupted or empty
**Action**: Run `python FIX_DATA.py`
**Result**: Automatic restoration from most recent backup

### Scenario 2: Selective Table Restoration
**When**: Only specific tables are corrupted
**Action**: Use `DataRecoverySystem` class with `tables` parameter
**Example**:
```python
recovery = DataRecoverySystem()
recovery.restore_from_backup(tables=['user', 'cadet'])
```

### Scenario 3: Backup Analysis
**When**: Need to understand what data is available
**Action**: Use `analyze_backup()` method
**Result**: Detailed breakdown of backup contents

### Scenario 4: Pre-Operation Backup
**When**: About to make risky changes
**Action**: Use `create_emergency_backup()`
**Result**: Safety snapshot before changes

## Error Handling and Recovery

### Common Issues and Solutions

#### 1. Database Connection Failures
**Cause**: Network issues, credential problems, database downtime
**Solution**: System provides detailed error messages and graceful failure

#### 2. Foreign Key Constraint Violations
**Cause**: Incorrect restoration order
**Solution**: System uses predefined table order and handles constraints

#### 3. Missing Backup Files
**Cause**: Backup directory empty or corrupted
**Solution**: System reports available backups and suggests alternatives

#### 4. Partial Restoration Failures
**Cause**: Some tables fail to restore
**Solution**: System continues with other tables and reports partial success

### Recovery Verification

After restoration, verify data integrity:
```python
# Check record counts
user_count = User.query.count()
cadet_count = Cadet.query.count()
print(f"Users: {user_count}, Cadets: {cadet_count}")
```

## Security Considerations

### Database Credentials
- **Current**: Hardcoded in recovery scripts
- **Risk**: Credentials exposed in source code
- **Recommendation**: Move to environment variables or secure credential storage

### Backup File Security
- **Location**: Local `backups/` directory
- **Access**: File system permissions
- **Recommendation**: Encrypt sensitive backup files

### Production Access
- **Scope**: Full database access for restoration
- **Risk**: Potential for data corruption during restoration
- **Mitigation**: Always create emergency backup before restoration

## Integration with Existing Systems

### Backup Scheduler Integration
The recovery system works alongside the existing `neon_backup_scheduler.py`:
- Scheduler creates regular backups
- Recovery system restores from these backups
- Both use the same JSON format

### Vercel Deployment
- Recovery scripts are deployed with the application
- Available for emergency use in production environment
- Can be run locally or on Vercel if needed

### Environment Variable Loading
The recovery system bypasses the environment variable loading issues that caused the original production failure by using hardcoded database URLs.

## Maintenance and Updates

### Regular Tasks
1. **Backup Verification**: Periodically test restoration from backups
2. **Credential Rotation**: Update database credentials when changed
3. **Format Validation**: Ensure backup files maintain correct JSON structure
4. **Performance Monitoring**: Monitor restoration times for large datasets

### Future Enhancements
1. **Incremental Backups**: Only backup changed data
2. **Compression**: Compress backup files to save space
3. **Encryption**: Encrypt sensitive backup data
4. **Cloud Storage**: Store backups in cloud storage (AWS S3, Google Cloud)
5. **Automated Testing**: Automated backup/restore testing
6. **Web Interface**: Web-based backup management interface

## Troubleshooting Guide

### Problem: "No backup files found"
**Solution**: Check `backups/` directory exists and contains `.json` files

### Problem: "Database connection failed"
**Solution**: Verify database URL is correct and database is accessible

### Problem: "Foreign key constraint violation"
**Solution**: Check table restoration order in `main_tables` list

### Problem: "Partial restoration completed"
**Solution**: Check individual table error messages and retry failed tables

### Problem: "Backup file corrupted"
**Solution**: Try older backup files or restore from database backup

## Best Practices

### Before Making Changes
1. Always create an emergency backup
2. Test changes in development environment
3. Have recovery plan ready

### During Recovery
1. Document what went wrong
2. Create backup before attempting recovery
3. Test recovery on small dataset first
4. Verify data integrity after recovery

### After Recovery
1. Investigate root cause of data loss
2. Implement preventive measures
3. Update documentation
4. Test backup/restore process

## Conclusion

The AFROTC 695 Data Recovery System provides a robust, reliable solution for protecting against data loss. While it was built in response to a specific incident, it serves as a comprehensive backup and recovery solution for the entire application.

The system's key strengths are:
- **Simplicity**: One-command emergency recovery
- **Reliability**: Direct database connection bypasses environment issues
- **Flexibility**: Supports both full and selective restoration
- **Transparency**: Detailed progress reporting and error handling

Regular testing and maintenance of this system ensures that data can be quickly recovered from any future incidents, minimizing downtime and data loss.

---

*Last Updated: August 17, 2025*
*System Version: 1.0*
*Created in response to production data loss incident*
