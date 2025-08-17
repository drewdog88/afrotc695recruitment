#!/usr/bin/env python3
"""
Examine external links data in backup file
"""

import json

def main():
    """Examine backup file for external links"""
    print("=== Examining Backup File for External Links ===")

    try:
        with open('backups/neon_backup_20250807_145537.json', 'r') as f:
            backup_data = json.load(f)

        print(f"Backup timestamp: {backup_data.get('timestamp')}")
        print(f"Total tables: {len(backup_data.get('tables', {}))}")

        # Check all tables
        tables = backup_data.get('tables', {})
        for table_name, table_data in tables.items():
            record_count = len(table_data) if isinstance(table_data, list) else 0
            print(f"  {table_name}: {record_count} records")

        # Specifically check external_link
        external_links = tables.get('external_link', [])
        print(f"\nExternal links in backup: {len(external_links)}")

        if external_links:
            print("\nExternal link details:")
            for i, link in enumerate(external_links, 1):
                print(f"\nLink {i}:")
                for key, value in link.items():
                    print(f"  {key}: {value}")
        else:
            print("No external links found in backup")

            # Check if there are any other link-related tables
            print("\nChecking for other link-related tables:")
            for table_name in tables.keys():
                if 'link' in table_name.lower():
                    print(f"  Found table: {table_name}")

    except Exception as e:
        print(f"❌ Error examining backup: {e}")

if __name__ == "__main__":
    main()
