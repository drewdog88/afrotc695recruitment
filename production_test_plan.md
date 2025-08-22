# Production Testing Plan - R2 Backup System

## 🎯 **Testing Objectives**
- Verify R2 backup system works in production environment
- Confirm security features are active
- Test backup creation, listing, and download functionality
- Validate all security vulnerabilities are patched

## 📋 **Phase 1: Deployment Verification**

### **1.1 Vercel Deployment Status**
- [ ] Check Vercel dashboard for successful deployment
- [ ] Verify build logs show no errors
- [ ] Confirm new version is live at production URL
- [ ] Check environment variables are properly set

### **1.2 Basic Application Health**
- [ ] Website loads without errors
- [ ] Admin login works correctly
- [ ] Database connectivity is functional
- [ ] No 500 errors in application logs

## 🧪 **Phase 2: R2 Backup System Testing**

### **2.1 R2 Connectivity Test**
```bash
# Test R2 connection from production
curl -X POST https://your-production-url.com/admin/test-r2-connection
```

**Expected Result**: Success response indicating R2 connectivity

### **2.2 Backup Creation Test**
1. **Login as Admin**
   - Navigate to admin dashboard
   - Verify admin privileges

2. **Create Daily Backup**
   - Go to backup management section
   - Click "Create Daily Backup"
   - Monitor for success message
   - Check backup appears in list

3. **Create Full Backup**
   - Click "Create Full Backup"
   - Monitor progress (may take 2-3 minutes)
   - Verify success message
   - Check backup appears in list

### **2.3 Backup Listing Test**
- [ ] View backup list shows recent backups
- [ ] Backup filenames follow correct pattern (`afrotc695_backup_*`)
- [ ] File sizes are reasonable (>0 bytes)
- [ ] Timestamps are current

### **2.4 Backup Download Test**
- [ ] Select a recent backup file
- [ ] Click download button
- [ ] Verify file downloads successfully
- [ ] Check file content is valid JSON/tar.gz
- [ ] Confirm file size matches listing

### **2.5 Security Validation Test**
- [ ] Try to access backup with invalid filename (`../../../etc/passwd`)
- [ ] Verify access is blocked with security error
- [ ] Check audit logs show security violation
- [ ] Confirm admin-only access (try without login)

## 🔒 **Phase 3: Security Verification**

### **3.1 Vulnerability Check**
```bash
# Check if security vulnerabilities are patched
# This should show no critical vulnerabilities
safety check --full-report
```

**Expected Result**: No critical vulnerabilities in cryptography, Pillow, or SQLAlchemy

### **3.2 Security Headers Test**
```bash
# Check security headers on backup download
curl -I https://your-production-url.com/admin/download-backup/test-file.json
```

**Expected Headers**:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`

### **3.3 Audit Logging Test**
- [ ] Check activity logs for backup operations
- [ ] Verify IP addresses are logged
- [ ] Confirm security violations are recorded
- [ ] Test unauthorized access attempts are logged

## 📊 **Phase 4: Performance & Reliability**

### **4.1 Backup Performance**
- [ ] Daily backup completes within 30 seconds
- [ ] Full backup completes within 5 minutes
- [ ] Download speeds are acceptable
- [ ] No timeout errors during operations

### **4.2 Error Handling**
- [ ] Test with invalid R2 credentials (should fail gracefully)
- [ ] Test with network issues (should show appropriate error)
- [ ] Verify error messages are user-friendly
- [ ] Check error logs for debugging information

## 🎯 **Success Criteria**

### **✅ All Tests Must Pass:**
- [ ] R2 connectivity established
- [ ] Backup creation works (daily and full)
- [ ] Backup listing shows correct files
- [ ] Backup download functions properly
- [ ] Security validation blocks invalid access
- [ ] No critical security vulnerabilities
- [ ] Security headers are present
- [ ] Audit logging is active
- [ ] Performance is acceptable

### **⚠️ Rollback Plan (If Issues Found):**
1. **Immediate**: Revert to previous deployment if critical issues
2. **Investigation**: Check logs for specific error details
3. **Fix**: Address issues in development environment
4. **Re-deploy**: Test fixes before production deployment

## 📝 **Testing Checklist**

### **Pre-Testing Setup**
- [ ] Admin credentials ready
- [ ] Production URL confirmed
- [ ] Testing environment prepared
- [ ] Rollback plan ready

### **During Testing**
- [ ] Document any errors or issues
- [ ] Take screenshots of success/failure states
- [ ] Note performance metrics
- [ ] Record security test results

### **Post-Testing**
- [ ] Verify all success criteria met
- [ ] Document any issues found
- [ ] Update deployment status
- [ ] Plan any follow-up actions

## 🚨 **Emergency Contacts**

If critical issues are found:
1. **Immediate**: Revert deployment via Vercel dashboard
2. **Investigation**: Check application logs and error reports
3. **Communication**: Update stakeholders on status

---

**Test Date**: _______________  
**Tester**: _______________  
**Results**: _______________
