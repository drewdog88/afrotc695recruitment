# Vercel Database Monitoring Deployment Guide

## 🎯 Overview

This guide explains how to deploy the database monitoring system on Vercel using cron jobs for continuous monitoring.

## 🚀 Deployment Strategies

### **Option 1: Vercel Cron Jobs (Recommended)**

Vercel supports cron jobs that run at scheduled intervals. This is perfect for database monitoring.

#### **Configuration:**

1. **Update `vercel.json`:**
```json
{
  "functions": {
    "api/cron/database-monitor.js": {
      "maxDuration": 30
    }
  },
  "crons": [
    {
      "path": "/api/cron/database-monitor",
      "schedule": "*/5 * * * *"
    }
  ]
}
```

2. **Cron Schedule Options:**
- `*/5 * * * *` - Every 5 minutes (recommended)
- `*/10 * * * *` - Every 10 minutes
- `0 */1 * * *` - Every hour
- `0 0 * * *` - Daily at midnight

#### **How It Works:**
- Vercel automatically calls the cron endpoint at the scheduled time
- The endpoint runs a single database check
- If anomalies are detected, email alerts are sent immediately
- The function completes and Vercel scales down

### **Option 2: External Cron Service**

Use an external service like cron-job.org or GitHub Actions.

#### **GitHub Actions Example:**
```yaml
name: Database Monitoring
on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run database monitoring
        run: python database_monitor.py --cron-check
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          ENABLE_EMAIL_ALERTS: true
          SMTP_SERVER: smtp.gmail.com
          SMTP_PORT: 587
          SMTP_USERNAME: ${{ secrets.SMTP_USERNAME }}
          SMTP_PASSWORD: ${{ secrets.SMTP_PASSWORD }}
          FROM_EMAIL: ${{ secrets.FROM_EMAIL }}
          TO_EMAILS: ${{ secrets.TO_EMAILS }}
```

### **Option 3: Cloudflare Workers Cron**

Use Cloudflare Workers for cron jobs.

## 📋 Environment Variables

Set these in your Vercel project settings:

```bash
# Database
DATABASE_URL=postgres://default:password@ep-cool-forest-123456.us-east-1.aws.neon.tech/neondb?sslmode=require

# Email Configuration
ENABLE_EMAIL_ALERTS=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=abrill1970@gmail.com
SMTP_PASSWORD=tygb ptnx tqhx ckrz
FROM_EMAIL=abrill1970@gmail.com
TO_EMAILS=abrill1970@gmail.com

# R2 Storage (for backups)
CLOUDFLARE_R2_ACCESS_KEY_ID=your-access-key
CLOUDFLARE_R2_SECRET_ACCESS_KEY=your-secret-key
CLOUDFLARE_R2_ACCOUNT_ID=your-account-id
```

## 🔧 Deployment Steps

### **1. Deploy to Vercel**
```bash
vercel --prod
```

### **2. Set Environment Variables**
```bash
vercel env add DATABASE_URL
vercel env add ENABLE_EMAIL_ALERTS
vercel env add SMTP_SERVER
vercel env add SMTP_PORT
vercel env add SMTP_USERNAME
vercel env add SMTP_PASSWORD
vercel env add FROM_EMAIL
vercel env add TO_EMAILS
```

### **3. Verify Cron Job**
```bash
vercel logs --follow
```

## 📊 Monitoring Dashboard

### **Vercel Dashboard:**
- Go to your project in Vercel dashboard
- Check "Functions" tab for cron job logs
- Monitor "Analytics" for function execution

### **Custom Dashboard:**
Access monitoring status via:
- `/api/cron/database-monitor` - Manual trigger
- `/admin/monitoring/status` - Status endpoint (if integrated)

## 🧪 Testing

### **Test Cron Job Locally:**
```bash
# Test the cron check
python database_monitor.py --cron-check

# Test the API endpoint
curl http://localhost:3000/api/cron/database-monitor
```

### **Test Email Alerts:**
```bash
python test_email_alerts.py
```

## 📈 Performance Considerations

### **Vercel Limits:**
- **Function timeout**: 30 seconds (cron jobs)
- **Memory**: 1024 MB
- **Cold starts**: May occur between executions

### **Optimizations:**
- Keep monitoring checks lightweight
- Use efficient database queries
- Minimize external API calls
- Cache baseline data

## 🔍 Troubleshooting

### **Common Issues:**

1. **Cron Job Not Running:**
   - Check Vercel dashboard for errors
   - Verify cron schedule syntax
   - Check function logs

2. **Email Not Sending:**
   - Verify SMTP credentials
   - Check Gmail app password
   - Test email configuration

3. **Database Connection Issues:**
   - Verify DATABASE_URL
   - Check Neon database status
   - Test connection locally

### **Debug Commands:**
```bash
# Check Vercel logs
vercel logs --follow

# Test database connection
python -c "from app import app, db; app.app_context().push(); print('DB connected')"

# Test email configuration
python test_email_alerts.py
```

## 🎯 Best Practices

### **1. Monitoring Frequency:**
- **Production**: Every 5-10 minutes
- **Development**: Every 30 minutes
- **Critical systems**: Every 1-2 minutes

### **2. Alert Thresholds:**
- **Record loss**: 10% threshold
- **Record gain**: 100% threshold
- **Suspicious operations**: Immediate alerts

### **3. Email Management:**
- Use Gmail for reliable delivery
- Set up multiple recipients for redundancy
- Monitor spam folders

### **4. Backup Strategy:**
- Keep monitoring logs in R2 storage
- Archive alert history
- Regular baseline updates

## 🚀 Production Checklist

- [ ] Environment variables configured
- [ ] Email alerts tested
- [ ] Cron job schedule set
- [ ] Monitoring baseline established
- [ ] Alert thresholds configured
- [ ] Logging enabled
- [ ] Backup system verified
- [ ] Performance tested

## 📞 Support

For issues with Vercel deployment:
1. Check Vercel dashboard logs
2. Test locally first
3. Verify environment variables
4. Check function timeout settings

---

**Your database monitoring system is now ready for production deployment on Vercel!** 🎉

