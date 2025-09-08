# Email Alert Setup Guide - AFROTC 695 Database Monitor

This guide explains how to configure email alerts for the database monitoring system.

## Environment Variables Required

Add these variables to your `.env` file:

```bash
# Email Configuration
ENABLE_EMAIL_ALERTS=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
TO_EMAILS=admin@afrotc695.com,backup-admin@afrotc695.com
```

## Gmail Setup (Recommended)

### 1. Enable 2-Factor Authentication
- Go to your Google Account settings
- Enable 2-Factor Authentication

### 2. Generate App Password
- Go to Google Account → Security → App passwords
- Generate a new app password for "Mail"
- Use this password as `SMTP_PASSWORD`

### 3. Configuration Example
```bash
ENABLE_EMAIL_ALERTS=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=afrotc695admin@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
FROM_EMAIL=afrotc695admin@gmail.com
TO_EMAILS=admin@afrotc695.com,commander@afrotc695.com
```

## Other Email Providers

### Outlook/Hotmail
```bash
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

### Yahoo
```bash
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

### Custom SMTP Server
```bash
SMTP_SERVER=your-smtp-server.com
SMTP_PORT=587
```

## Testing Email Configuration

Run the test script to verify your email setup:

```bash
python test_email_alerts.py
```

## Alert Types

The system will send email alerts for:

1. **SUSPICIOUS_OPERATION**: TRUNCATE, DROP, DELETE FROM operations
2. **RECORD_LOSS**: When 10% or more records are lost from any table
3. **RECORD_GAIN**: When records double in any table

## Email Content

Alerts include:
- Alert type and timestamp
- Detailed message
- Technical details (SQL statements, record counts)
- Instructions to investigate

## Security Considerations

1. **Use App Passwords**: Never use your main password
2. **Restrict Access**: Only send to authorized email addresses
3. **Monitor Alerts**: Regularly check alert logs
4. **Backup Configuration**: Keep email config in secure location

## Troubleshooting

### Common Issues:

1. **Authentication Failed**
   - Check username/password
   - Ensure 2FA is enabled for Gmail
   - Use app password, not main password

2. **Connection Refused**
   - Check SMTP server and port
   - Verify firewall settings
   - Try different port (465 for SSL)

3. **No Emails Received**
   - Check spam folder
   - Verify TO_EMAILS format (comma-separated)
   - Check ENABLE_EMAIL_ALERTS=true

### Test Commands:

```bash
# Test email configuration
python -c "from database_monitor import DatabaseMonitor; m = DatabaseMonitor(); print('Email config:', m.email_config)"

# Test email sending
python test_email_alerts.py
```

## Integration with Application

To integrate email alerts with your Flask application:

```python
from database_monitor import DatabaseMonitor

# Initialize monitor
monitor = DatabaseMonitor()

# Start monitoring in background
monitor.start_monitoring(interval_seconds=300)  # Check every 5 minutes
```

## Monitoring Dashboard

The system creates these log files:
- `logs/database_monitor.log` - All monitoring activity
- `logs/database_alerts.json` - Alert history
- `logs/baseline_counts.json` - Baseline record counts

## Alert Frequency

- **Immediate**: Suspicious operations (TRUNCATE, DROP, DELETE)
- **Every Check**: Record loss/gain anomalies
- **Configurable**: Adjust `interval_seconds` in `start_monitoring()`

## Best Practices

1. **Test First**: Always test email configuration before production
2. **Monitor Logs**: Regularly check monitoring logs
3. **Update Contacts**: Keep TO_EMAILS list current
4. **Backup Alerts**: Archive alert history regularly
5. **Review Thresholds**: Adjust alert thresholds as needed


