#!/usr/bin/env python3
"""
AFROTC 695 Database Monitoring System
Monitors database changes, record counts, and provides alerting for suspicious activity
"""

import os
import json
import time
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from sqlalchemy import text, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/database_monitor.log'),
        logging.StreamHandler()
    ]
)

class DatabaseMonitor:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL not found in environment variables")

        # Convert postgres:// to postgresql:// for SQLAlchemy
        if self.database_url.startswith('postgres://'):
            self.database_url = self.database_url.replace('postgres://', 'postgresql://', 1)

        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)

        # Monitoring state
        self.baseline_counts = {}
        self.alert_thresholds = {
            'record_loss_threshold': 0.1,  # Alert if 10% of records lost
            'record_gain_threshold': 2.0,  # Alert if records double
            'suspicious_operations': ['TRUNCATE', 'DROP', 'DELETE FROM']
        }

        # Alert history
        self.alerts = []
        self.monitoring_active = False

        # Email configuration
        self.email_config = {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'smtp_username': os.getenv('SMTP_USERNAME'),
            'smtp_password': os.getenv('SMTP_PASSWORD'),
            'from_email': os.getenv('FROM_EMAIL'),
            'to_emails': os.getenv('TO_EMAILS', '').split(','),
            'enable_email': os.getenv('ENABLE_EMAIL_ALERTS', 'false').lower() == 'true'
        }

        # Setup database event listeners
        self.setup_event_listeners()

    def setup_event_listeners(self):
        """Setup SQLAlchemy event listeners to track database operations"""
        @event.listens_for(self.engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """Log all SQL operations before execution"""
            if self.monitoring_active:
                self.log_operation(statement, parameters, 'BEFORE_EXECUTE')

        @event.listens_for(self.engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """Log all SQL operations after execution"""
            if self.monitoring_active:
                self.log_operation(statement, parameters, 'AFTER_EXECUTE')

    def log_operation(self, statement, parameters, operation_type):
        """Log database operations"""
        try:
            # Check for suspicious operations
            statement_upper = statement.upper()
            for suspicious_op in self.alert_thresholds['suspicious_operations']:
                if suspicious_op in statement_upper:
                    self.create_alert(
                        'SUSPICIOUS_OPERATION',
                        f'Detected suspicious operation: {suspicious_op}',
                        {
                            'statement': statement,
                            'parameters': str(parameters),
                            'operation_type': operation_type
                        }
                    )

            # Log the operation
            logging.info(f"DB Operation [{operation_type}]: {statement[:100]}...")

        except Exception as e:
            logging.error(f"Error logging operation: {e}")

    def get_table_counts(self):
        """Get current record counts for all tables"""
        try:
            session = self.Session()

            # List of tables to monitor
            tables = [
                'user', 'potential_recruit', 'cadet', 'university_contact',
                'recruitment_event', 'external_link', 'recruitment_document',
                'activity_log', 'password_history'
            ]

            counts = {}
            for table in tables:
                try:
                    result = session.execute(text(f'SELECT COUNT(*) FROM "{table}"'))
                    count = result.scalar()
                    counts[table] = count
                except Exception as e:
                    logging.warning(f"Could not get count for table {table}: {e}")
                    counts[table] = 0

            session.close()
            return counts

        except Exception as e:
            logging.error(f"Error getting table counts: {e}")
            return {}

    def establish_baseline(self):
        """Establish baseline record counts"""
        logging.info("Establishing baseline record counts...")
        self.baseline_counts = self.get_table_counts()

        logging.info("Baseline counts established:")
        for table, count in self.baseline_counts.items():
            logging.info(f"  {table}: {count} records")

        # Save baseline to file
        self.save_baseline()

    def save_baseline(self):
        """Save baseline counts to file"""
        try:
            baseline_data = {
                'timestamp': datetime.now().isoformat(),
                'counts': self.baseline_counts
            }

            os.makedirs('logs', exist_ok=True)
            with open('logs/baseline_counts.json', 'w') as f:
                json.dump(baseline_data, f, indent=2)

            logging.info("Baseline saved to logs/baseline_counts.json")

        except Exception as e:
            logging.error(f"Error saving baseline: {e}")

    def load_baseline(self):
        """Load baseline counts from file"""
        try:
            baseline_file = 'logs/baseline_counts.json'
            if os.path.exists(baseline_file):
                with open(baseline_file, 'r') as f:
                    baseline_data = json.load(f)

                self.baseline_counts = baseline_data['counts']
                logging.info(f"Loaded baseline from {baseline_data['timestamp']}")
                return True
            else:
                logging.warning("No baseline file found")
                return False

        except Exception as e:
            logging.error(f"Error loading baseline: {e}")
            return False

    def check_for_anomalies(self):
        """Check current counts against baseline for anomalies"""
        if not self.baseline_counts:
            logging.warning("No baseline established, skipping anomaly check")
            return

        current_counts = self.get_table_counts()

        for table in self.baseline_counts:
            if table not in current_counts:
                continue

            baseline_count = self.baseline_counts[table]
            current_count = current_counts[table]

            if baseline_count == 0:
                continue

            # Calculate percentage change
            if baseline_count > 0:
                percentage_change = (current_count - baseline_count) / baseline_count
            else:
                percentage_change = 0

            # Check for significant record loss
            if percentage_change < -self.alert_thresholds['record_loss_threshold']:
                self.create_alert(
                    'RECORD_LOSS',
                    f'Significant record loss detected in {table}',
                    {
                        'table': table,
                        'baseline_count': baseline_count,
                        'current_count': current_count,
                        'percentage_change': percentage_change,
                        'records_lost': baseline_count - current_count
                    }
                )

            # Check for suspicious record gain
            elif percentage_change > self.alert_thresholds['record_gain_threshold']:
                self.create_alert(
                    'RECORD_GAIN',
                    f'Unusual record gain detected in {table}',
                    {
                        'table': table,
                        'baseline_count': baseline_count,
                        'current_count': current_count,
                        'percentage_change': percentage_change,
                        'records_gained': current_count - baseline_count
                    }
                )

    def create_alert(self, alert_type, message, details):
        """Create and log an alert"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'message': message,
            'details': details
        }

        self.alerts.append(alert)

        # Log the alert
        logging.warning(f"ALERT [{alert_type}]: {message}")
        logging.warning(f"Alert details: {json.dumps(details, indent=2)}")

        # Save alert to file
        self.save_alerts()

        # Send immediate notification
        self.send_notification(alert)

    def save_alerts(self):
        """Save alerts to file"""
        try:
            os.makedirs('logs', exist_ok=True)
            with open('logs/database_alerts.json', 'w') as f:
                json.dump(self.alerts, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving alerts: {e}")

    def send_email_alert(self, alert):
        """Send email alert"""
        if not self.email_config['enable_email']:
            logging.info("Email alerts disabled")
            return

        if not all([
            self.email_config['smtp_username'],
            self.email_config['smtp_password'],
            self.email_config['from_email'],
            self.email_config['to_emails']
        ]):
            logging.warning("Email configuration incomplete, skipping email alert")
            return

        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = ', '.join(self.email_config['to_emails'])
            msg['Subject'] = f"🚨 Database Alert: {alert['type']} - AFROTC 695"

            # Create email body
            body = f"""
🚨 DATABASE ALERT - AFROTC 695 Recruitment System

Alert Type: {alert['type']}
Time: {alert['timestamp']}
Message: {alert['message']}

Details:
{json.dumps(alert['details'], indent=2)}

This is an automated alert from the AFROTC 695 Database Monitoring System.
Please investigate this issue immediately.

---
AFROTC 695 Database Monitor
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """

            msg.attach(MIMEText(body, 'plain'))

            # Send email
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['smtp_username'], self.email_config['smtp_password'])
                server.send_message(msg)

            logging.info(f"Email alert sent to {', '.join(self.email_config['to_emails'])}")

        except Exception as e:
            logging.error(f"Error sending email alert: {e}")

    def send_notification(self, alert):
        """Send notification for critical alerts"""
        # Log critical alerts
        if alert['type'] in ['SUSPICIOUS_OPERATION', 'RECORD_LOSS']:
            logging.critical(f"CRITICAL ALERT: {alert['message']}")

        # Send email alert
        self.send_email_alert(alert)

    def start_monitoring(self, interval_seconds=60):
        """Start continuous monitoring"""
        if self.monitoring_active:
            logging.warning("Monitoring already active")
            return

        # Load or establish baseline
        if not self.load_baseline():
            self.establish_baseline()

        self.monitoring_active = True
        logging.info(f"Starting database monitoring (checking every {interval_seconds} seconds)")

        def monitor_loop():
            while self.monitoring_active:
                try:
                    self.check_for_anomalies()
                    time.sleep(interval_seconds)
                except Exception as e:
                    logging.error(f"Error in monitoring loop: {e}")
                    time.sleep(interval_seconds)

        # Start monitoring in background thread
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        logging.info("Database monitoring stopped")

    def get_status(self):
        """Get current monitoring status"""
        current_counts = self.get_table_counts()

        status = {
            'monitoring_active': self.monitoring_active,
            'baseline_timestamp': None,
            'current_counts': current_counts,
            'recent_alerts': self.alerts[-5:] if self.alerts else [],
            'total_alerts': len(self.alerts),
            'email_enabled': self.email_config['enable_email']
        }

        # Load baseline timestamp
        try:
            baseline_file = 'logs/baseline_counts.json'
            if os.path.exists(baseline_file):
                with open(baseline_file, 'r') as f:
                    baseline_data = json.load(f)
                status['baseline_timestamp'] = baseline_data['timestamp']
        except Exception:
            pass

        return status

def main():
    """Main function for testing the monitor"""
    try:
        monitor = DatabaseMonitor()

        print("Database Monitor Test")
        print("=" * 50)

        # Get current status
        status = monitor.get_status()
        print(f"Monitoring Active: {status['monitoring_active']}")
        print(f"Total Alerts: {status['total_alerts']}")
        print(f"Email Alerts: {'Enabled' if status['email_enabled'] else 'Disabled'}")

        # Show current counts
        print("\nCurrent Table Counts:")
        for table, count in status['current_counts'].items():
            print(f"  {table}: {count} records")

        # Show recent alerts
        if status['recent_alerts']:
            print("\nRecent Alerts:")
            for alert in status['recent_alerts']:
                print(f"  [{alert['type']}] {alert['message']}")

        # Start monitoring
        print("\nStarting monitoring...")
        monitor.start_monitoring(interval_seconds=30)  # Check every 30 seconds

        print("Monitoring started. Press Ctrl+C to stop.")

        try:
            while True:
                time.sleep(10)
                # Print status every 10 seconds
                status = monitor.get_status()
                if status['recent_alerts']:
                    print(f"New alerts: {len(status['recent_alerts'])}")
        except KeyboardInterrupt:
            print("\nStopping monitoring...")
            monitor.stop_monitoring()

    except Exception as e:
        logging.error(f"Error in main: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    import sys

    # Check if running in cron mode
    if "--cron-check" in sys.argv:
        # Run a single check for cron jobs
        try:
            monitor = DatabaseMonitor()
            # Load baseline if it exists, otherwise establish one
            if not monitor.load_baseline():
                monitor.establish_baseline()
            monitor.check_for_anomalies()
            print("Cron check completed successfully")
        except Exception as e:
            print(f"Cron check failed: {e}")
            sys.exit(1)
    else:
        # Run interactive mode
        main()
