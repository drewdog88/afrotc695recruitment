#!/usr/bin/env python3
"""
Check backup file structure
"""

import json

def main():
    """Check backup structure"""
    with open('backups/neon_backup_20250807_145537.json', 'r') as f:
        data = json.load(f)
    
    print("=== Backup File Structure ===")
    print(f"Backup timestamp: {data['metadata']['backup_timestamp']}")
    print(f"Total tables: {data['metadata']['total_tables']}")
    print(f"Total records: {data['metadata']['total_records']}")
    print()
    
    print("Tables in backup:")
    for table_name, table_info in data['tables'].items():
        print(f"  {table_name}: {table_info['record_count']} records")
    
    print()
    print("Sample data from each table:")
    for table_name, table_info in data['tables'].items():
        if table_info['data']:
            print(f"\n{table_name} (first record):")
            first_record = table_info['data'][0]
            for key, value in first_record.items():
                print(f"  {key}: {value}")

if __name__ == "__main__":
    main()
