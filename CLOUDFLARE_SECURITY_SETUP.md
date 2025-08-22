# Cloudflare R2 Security Setup for AFROTC 695

## **🛡️ Military-Grade Security Implementation**

This document outlines the security measures required for protecting military recruitment data stored in Cloudflare R2.

## **Required Environment Variables**

### **Current R2 Variables (Required)**
```bash
CLOUDFLARE_R2_ACCOUNT_ID=your_account_id
CLOUDFLARE_R2_ACCESS_KEY_ID=your_access_key_id
CLOUDFLARE_R2_SECRET_ACCESS_KEY=your_secret_access_key
```

### **Enhanced Security Variable (Recommended)**
```bash
CLOUDFLARE_R2_CUSTOM_DOMAIN=backups.afrotc695.com
```

## **Cloudflare Dashboard Setup**

### **Step 1: Configure Custom Domain**
1. Go to **Cloudflare Dashboard** → **R2 Object Storage**
2. Select bucket: `afrotc695recruitment`
3. **Add Custom Domain**: `backups.afrotc695.com`
4. **Enable Proxy**: Ensure orange cloud icon is active
5. **SSL/TLS**: Set to "Full (strict)"

### **Step 2: Set Up Cloudflare Access (Zero Trust)**
1. Go to **Cloudflare Dashboard** → **Zero Trust** → **Access**
2. **Create Application**:
   - Name: `AFROTC R2 Storage`
   - Type: `Self-hosted`
   - Domain: `backups.afrotc695.com`
3. **Configure Policies**:
   - **Service Auth**: Allow only your Vercel deployment
   - **IP Restrictions**: Restrict to Vercel IP ranges
   - **Authentication**: Require valid session tokens

### **Step 3: Configure Security Headers**
1. Go to **Cloudflare Dashboard** → **Security** → **WAF**
2. **Create Custom Rule**:
   - Name: `AFROTC R2 Security`
   - Field: `URI Path`
   - Operator: `contains`
   - Value: `afrotc695_backup_`
   - Action: `Block` (for unauthorized access)

## **Security Features Implemented**

### **✅ Server-Side Proxy**
- No direct R2 URLs exposed to users
- All access through authenticated web backend
- Credentials never leave server

### **✅ Enhanced Authentication**
- Admin-only access with session validation
- IP address logging and tracking
- Comprehensive audit trail

### **✅ File Validation**
- Only backup files allowed (`afrotc695_backup_*`)
- Path traversal protection (`..` blocked)
- MIME type validation

### **✅ Security Headers**
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`
- `Content-Security-Policy: default-src 'self'`

### **✅ Audit Logging**
- All access attempts logged
- Security violations tracked
- IP addresses and user agents recorded
- File access details captured

## **Deployment Checklist**

- [ ] Set `CLOUDFLARE_R2_CUSTOM_DOMAIN` environment variable
- [ ] Configure custom domain in Cloudflare R2
- [ ] Set up Cloudflare Access (Zero Trust)
- [ ] Configure WAF rules
- [ ] Test backup download functionality
- [ ] Verify security headers are present
- [ ] Confirm audit logging is working

## **Security Monitoring**

### **Regular Checks**
- Monitor access logs for unauthorized attempts
- Review audit trail for suspicious activity
- Verify custom domain is active and proxied
- Check Cloudflare Access policies are enforced

### **Incident Response**
- All security violations are logged with IP addresses
- Failed access attempts trigger immediate alerts
- Unauthorized file access attempts are blocked
- Comprehensive audit trail for investigation

## **Compliance**

This implementation follows:
- **Cloudflare Security Best Practices**
- **Military Data Protection Standards**
- **Zero Trust Security Model**
- **Defense in Depth Principles**

---

**⚠️ IMPORTANT**: This system contains military recruitment data and must be treated with the highest level of security. All access is logged and monitored.
