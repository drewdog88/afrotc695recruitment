#!/usr/bin/env python3
"""
Setup script for local MySQL database to match production environment
"""

import subprocess
import sys
import os

def run_mysql_command(command, password=None):
    """Run a MySQL command"""
    try:
        if password:
            # Use subprocess with password input
            process = subprocess.Popen(
                ['mysql', '-u', 'root', '-p' + password],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(input=command)
        else:
            # Try without password first
            process = subprocess.run(
                ['mysql', '-u', 'root'] + command.split(),
                capture_output=True,
                text=True
            )
            stdout, stderr = process.stdout, process.stderr
            
        if process.returncode != 0:
            print(f"Error: {stderr}")
            return False
        return True
    except Exception as e:
        print(f"Error running MySQL command: {e}")
        return False

def setup_database():
    """Set up the database and user"""
    print("Setting up local MySQL database to match production...")
    
    # Database and user details (matching production)
    db_name = "cascznjx_afrotc_recruit"
    db_user = "cascznjx_afrotcdbadmin"
    db_password = "E3@8SXMxNPHG"
    
    # SQL commands to set up database and user
    setup_commands = [
        f"CREATE DATABASE IF NOT EXISTS `{db_name}`;",
        f"CREATE USER IF NOT EXISTS '{db_user}'@'localhost' IDENTIFIED BY '{db_password}';",
        f"GRANT ALL PRIVILEGES ON `{db_name}`.* TO '{db_user}'@'localhost';",
        "FLUSH PRIVILEGES;"
    ]
    
    print("Please enter your MySQL root password (or press Enter if no password):")
    root_password = input().strip()
    
    if not root_password:
        root_password = None
    
    for command in setup_commands:
        print(f"Running: {command}")
        if run_mysql_command(command, root_password):
            print("✓ Success")
        else:
            print("✗ Failed")
            return False
    
    print(f"\nDatabase setup complete!")
    print(f"Database: {db_name}")
    print(f"User: {db_user}")
    print(f"Password: {db_password}")
    print(f"\nYou can now run: python app_production.py")
    
    return True

if __name__ == "__main__":
    setup_database() 