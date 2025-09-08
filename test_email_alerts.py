#!/usr/bin/env python3
"""
Test script for email alert functionality
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from database_monitor import DatabaseMonitor

def test_email_configuration():
    """Test email configuration"""
    print("Testing Email Configuration")
    print("=" * 50)

    try:
        monitor = DatabaseMonitor()

        print("Email Configuration:")
        print(f"  SMTP Server: {monitor.email_config['smtp_server']}")
        print(f"  SMTP Port: {monitor.email_config['smtp_port']}")
        print(f"  Username: {monitor.email_config['smtp_username']}")
        print(f"  From Email: {monitor.email_config['from_email']}")
        print(f"  To Emails: {monitor.email_config['to_emails']}")
        print(f"  Enabled: {monitor.email_config['enable_email']}")

        # Check if all required fields are set
        required_fields = ['smtp_username', 'smtp_password', 'from_email', 'to_emails']
        missing_fields = []

        for field in required_fields:
            if not monitor.email_config[field]:
                missing_fields.append(field)

        if missing_fields:
            print(f"\n❌ Missing required fields: {', '.join(missing_fields)}")
            print("Please check your .env file configuration")
            return False
        else:
            print("\n✅ All required email fields are configured")
            return True

    except Exception as e:
        print(f"❌ Error testing email configuration: {e}")
        return False

def test_email_sending():
    """Test sending a test email"""
    print("\nTesting Email Sending")
    print("=" * 50)

    try:
        monitor = DatabaseMonitor()

        if not monitor.email_config['enable_email']:
            print("❌ Email alerts are disabled")
            print("Set ENABLE_EMAIL_ALERTS=true in your .env file")
            return False

        # Create a test alert
        test_alert = {
            'timestamp': datetime.now().isoformat(),
            'type': 'TEST_ALERT',
            'message': 'This is a test email alert from AFROTC 695 Database Monitor',
            'details': {
                'test': True,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'system': 'AFROTC 695 Database Monitor'
            }
        }

        print("Sending test email alert...")
        monitor.send_email_alert(test_alert)

        print("✅ Test email sent successfully!")
        print("Check your email inbox for the test message")
        return True

    except Exception as e:
        print(f"❌ Error sending test email: {e}")
        return False

def test_database_monitoring():
    """Test database monitoring functionality"""
    print("\nTesting Database Monitoring")
    print("=" * 50)

    try:
        monitor = DatabaseMonitor()

        # Get current status
        status = monitor.get_status()

        print("Database Status:")
        print(f"  Monitoring Active: {status['monitoring_active']}")
        print(f"  Total Alerts: {status['total_alerts']}")
        print(f"  Email Enabled: {status['email_enabled']}")

        print("\nCurrent Table Counts:")
        for table, count in status['current_counts'].items():
            print(f"  {table}: {count} records")

        # Establish baseline
        print("\nEstablishing baseline...")
        monitor.establish_baseline()

        print("✅ Database monitoring test completed")
        return True

    except Exception as e:
        print(f"❌ Error testing database monitoring: {e}")
        return False

def show_environment_check():
    """Show current environment variables"""
    print("Environment Variables Check")
    print("=" * 50)

    load_dotenv()

    email_vars = [
        'ENABLE_EMAIL_ALERTS',
        'SMTP_SERVER',
        'SMTP_PORT',
        'SMTP_USERNAME',
        'SMTP_PASSWORD',
        'FROM_EMAIL',
        'TO_EMAILS'
    ]

    for var in email_vars:
        value = os.getenv(var)
        if var == 'SMTP_PASSWORD' and value:
            value = '*' * len(value)  # Hide password
        print(f"  {var}: {value or 'NOT SET'}")

    print(f"  DATABASE_URL: {'SET' if os.getenv('DATABASE_URL') else 'NOT SET'}")

def main():
    """Main test function"""
    print("AFROTC 695 Database Monitor - Email Alert Test")
    print("=" * 60)

    # Show environment check
    show_environment_check()

    # Test email configuration
    config_ok = test_email_configuration()

    if config_ok:
        # Test email sending
        email_ok = test_email_sending()

        if email_ok:
            # Test database monitoring
            monitor_ok = test_database_monitoring()

            if monitor_ok:
                print("\n🎉 All tests passed! Email alerts are working correctly.")
                print("\nNext steps:")
                print("1. Start monitoring: python database_monitor.py")
                print("2. Check logs: tail -f logs/database_monitor.log")
                print("3. View alerts: cat logs/database_alerts.json")
            else:
                print("\n❌ Database monitoring test failed")
        else:
            print("\n❌ Email sending test failed")
    else:
        print("\n❌ Email configuration test failed")
        print("\nPlease check EMAIL_SETUP_GUIDE.md for configuration instructions")

if __name__ == "__main__":
    main()


