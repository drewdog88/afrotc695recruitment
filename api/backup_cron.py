# Vercel CRON function for automated backup
import os
import json
import boto3
from datetime import datetime
from sqlalchemy import create_engine, text

def handler(request):
    """Vercel serverless function for automated backup"""
    try:
        # Get database URL
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'DATABASE_URL not configured'})
            }
        
        # Get R2 credentials
        r2_access_key = os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID')
        r2_secret_key = os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY')
        r2_bucket = os.getenv('CLOUDFLARE_R2_BUCKET_NAME', 'afrotc695-backups')
        
        if not r2_access_key or not r2_secret_key:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'R2 credentials not configured'})
            }
        
        print(f"Starting automated backup at {datetime.now().isoformat()}")
        
        # Create database connection
        engine = create_engine(database_url)
        
        # Get all tables
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
            """))
            tables = [row[0] for row in result]
        
        # Create backup data
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'tables': {}
        }
        
        # Backup each table
        with engine.connect() as conn:
            for table in tables:
                result = conn.execute(text(f"SELECT * FROM {table}"))
                rows = result.fetchall()
                columns = result.keys()
                
                backup_data['tables'][table] = {
                    'columns': list(columns),
                    'rows': [dict(row._mapping) for row in rows]
                }
                
                print(f"Backed up {len(rows)} records from {table}")
        
        # Upload to R2
        s3_client = boto3.client(
            's3',
            endpoint_url='https://kre9xoivjggj03of.public.blob.vercel-storage.com',
            aws_access_key_id=r2_access_key,
            aws_secret_access_key=r2_secret_key
        )
        
        backup_filename = f"afrotc695_backup_cron_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        s3_client.put_object(
            Bucket=r2_bucket,
            Key=backup_filename,
            Body=json.dumps(backup_data, indent=2),
            ContentType='application/json'
        )
        
        print(f"Backup uploaded successfully: {backup_filename}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'backup_filename': backup_filename,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        print(f"Backup error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }
