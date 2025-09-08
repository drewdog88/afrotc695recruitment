#!/usr/bin/env python3
"""
Integration script to add database monitoring to the Flask application
"""

import threading
import time
from database_monitor import DatabaseMonitor

def start_database_monitoring(app):
    """Start database monitoring in a background thread"""

    def monitor_thread():
        """Background thread for database monitoring"""
        try:
            monitor = DatabaseMonitor()

            # Start monitoring with 5-minute intervals
            monitor.start_monitoring(interval_seconds=300)

            # Keep the thread alive
            while True:
                time.sleep(60)  # Check every minute if monitoring is still active
                if not monitor.monitoring_active:
                    break

        except Exception as e:
            print(f"Database monitoring error: {e}")

    # Start monitoring in background thread
    monitor_thread = threading.Thread(target=monitor_thread, daemon=True)
    monitor_thread.start()

    print("Database monitoring started in background thread")
    return monitor_thread

def add_monitoring_routes(app):
    """Add monitoring routes to Flask app"""

    @app.route('/admin/monitoring/status')
    def monitoring_status():
        """Get monitoring status"""
        try:
            monitor = DatabaseMonitor()
            status = monitor.get_status()

            return {
                'monitoring_active': status['monitoring_active'],
                'total_alerts': status['total_alerts'],
                'email_enabled': status['email_enabled'],
                'current_counts': status['current_counts'],
                'recent_alerts': status['recent_alerts'][-10:],  # Last 10 alerts
                'baseline_timestamp': status['baseline_timestamp']
            }
        except Exception as e:
            return {'error': str(e)}, 500

    @app.route('/admin/monitoring/start')
    def start_monitoring():
        """Start database monitoring"""
        try:
            monitor = DatabaseMonitor()
            monitor.start_monitoring(interval_seconds=300)
            return {'message': 'Database monitoring started'}
        except Exception as e:
            return {'error': str(e)}, 500

    @app.route('/admin/monitoring/stop')
    def stop_monitoring():
        """Stop database monitoring"""
        try:
            monitor = DatabaseMonitor()
            monitor.stop_monitoring()
            return {'message': 'Database monitoring stopped'}
        except Exception as e:
            return {'error': str(e)}, 500

    @app.route('/admin/monitoring/baseline')
    def establish_baseline():
        """Establish new baseline"""
        try:
            monitor = DatabaseMonitor()
            monitor.establish_baseline()
            return {'message': 'Baseline established'}
        except Exception as e:
            return {'error': str(e)}, 500

def integrate_with_app():
    """Main integration function"""
    print("Database Monitoring Integration")
    print("=" * 40)

    # Test monitor initialization
    try:
        monitor = DatabaseMonitor()
        print("✅ Database monitor initialized successfully")

        # Show current status
        status = monitor.get_status()
        print(f"Current record counts: {status['current_counts']}")
        print(f"Email alerts: {'Enabled' if status['email_enabled'] else 'Disabled'}")

        # Establish baseline
        print("Establishing baseline...")
        monitor.establish_baseline()
        print("✅ Baseline established")

        return True

    except Exception as e:
        print(f"❌ Integration failed: {e}")
        return False

if __name__ == "__main__":
    integrate_with_app()


