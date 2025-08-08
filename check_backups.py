#!/usr/bin/env python3
from app_local import get_backup_files, app

with app.app_context():
    files = get_backup_files()
    print(f'Total backups: {len(files)}')
    for i, f in enumerate(files):
        print(f'{i+1}. {f["filename"]} - {f["created"]}')
