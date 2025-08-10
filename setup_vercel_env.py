#!/usr/bin/env python3
"""
Vercel Environment Variables Setup Script
This script helps you set up the required environment variables for your Vercel deployment.
"""

import os
import json
from pathlib import Path

def load_env_file(file_path):
    """Load environment variables from a .env file"""
    env_vars = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    return env_vars

def generate_vercel_commands(env_vars):
    """Generate Vercel CLI commands to set environment variables"""
    commands = []
    
    # Required variables for production
    required_vars = [
        'DATABASE_URL',
        'BLOB_READ_WRITE_TOKEN', 
        'SECRET_KEY',
        'TOTP_ENCRYPTION_KEY',
        'BCRYPT_ROUNDS',
        'FLASK_ENV'
    ]
    
    print("🔧 Vercel Environment Variables Setup")
    print("=" * 50)
    print()
    print("📋 REQUIRED ENVIRONMENT VARIABLES:")
    print()
    
    for var in required_vars:
        if var in env_vars:
            value = env_vars[var]
            if var in ['SECRET_KEY', 'TOTP_ENCRYPTION_KEY', 'BLOB_READ_WRITE_TOKEN']:
                # Mask sensitive values
                masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
            
            # Generate Vercel CLI command
            command = f'vercel env add {var} production'
            commands.append(command)
        else:
            print(f"❌ {var}: MISSING")
            print(f"   Command: vercel env add {var} production")
            commands.append(f'vercel env add {var} production')
    
    print()
    print("🚀 VERCEL CLI COMMANDS TO RUN:")
    print("=" * 50)
    print()
    print("# Run these commands in your terminal:")
    print()
    
    for i, command in enumerate(commands, 1):
        print(f"{i}. {command}")
        if command in ['vercel env add SECRET_KEY production', 'vercel env add TOTP_ENCRYPTION_KEY production']:
            print("   # You'll be prompted to enter the value securely")
        elif command == 'vercel env add BLOB_READ_WRITE_TOKEN production':
            print("   # Enter: vercel_blob_rw_pWMALcxzCqU5EtRO_nz6sr9gFjTvtBizz3PfMYiv8efYDNe")
        elif command == 'vercel env add DATABASE_URL production':
            print("   # Enter: postgresql://neondb_owner:npg_5qC7jUoluvOY@ep-crimson-hall-admf1mo5-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require")
        elif command == 'vercel env add BCRYPT_ROUNDS production':
            print("   # Enter: 12")
        elif command == 'vercel env add FLASK_ENV production':
            print("   # Enter: production")
        print()
    
    print("📝 ALTERNATIVE: Manual Dashboard Setup")
    print("=" * 50)
    print()
    print("If you prefer to use the Vercel dashboard:")
    print("1. Go to https://vercel.com/dashboard")
    print("2. Select your project")
    print("3. Go to Settings → Environment Variables")
    print("4. Add each variable manually")
    print()
    
    return commands

def main():
    """Main function"""
    # Load environment variables from env.local
    env_vars = load_env_file('env.local')
    
    if not env_vars:
        print("❌ No environment variables found in env.local")
        print("Please make sure env.local exists and contains the required variables.")
        return
    
    # Generate commands
    commands = generate_vercel_commands(env_vars)
    
    # Save commands to file for easy reference
    with open('vercel_env_setup_commands.txt', 'w') as f:
        f.write("Vercel Environment Variables Setup Commands\n")
        f.write("=" * 50 + "\n\n")
        f.write("Run these commands in your terminal:\n\n")
        for i, command in enumerate(commands, 1):
            f.write(f"{i}. {command}\n")
    
    print("💾 Commands saved to: vercel_env_setup_commands.txt")
    print()
    print("🎯 NEXT STEPS:")
    print("1. Run the Vercel CLI commands above")
    print("2. Redeploy your application: vercel --prod")
    print("3. Test the /admin and /recruits routes")
    print()
    print("✅ This should fix your production deployment issues!")

if __name__ == "__main__":
    main()
