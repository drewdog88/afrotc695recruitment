# Environment Variables Guide - AFROTC 695 Recruitment System

## CRITICAL: READ THIS FIRST IN EVERY SESSION

This document explains how environment variables work in this project to prevent recurring failures.

## Environment Variable Storage Locations

### 1. Production Environment (Vercel)
- **Location**: Vercel dashboard → Project Settings → Environment Variables
- **Access**: Only available when deployed to Vercel
- **Purpose**: Production credentials and configuration
- **Variables**: All sensitive data (API keys, database URLs, etc.)

### 2. Local Development Environment
- **Location**: `.env` file in project root
- **Access**: Via `dotenv` library
- **Purpose**: Local development and testing
- **Loading**: `load_dotenv()` in `conftest.py` and application startup

## Environment Variable Loading Process

### Application Startup
```python
from dotenv import load_dotenv
load_dotenv()  # Loads from .env file
```

### Test Environment
```python
# In tests/conftest.py
from dotenv import load_dotenv
load_dotenv()  # Loads from .env file for tests
```

## Key Environment Variables

### Required for Local Development
- `CLOUDFLARE_R2_ACCESS_KEY_ID` - Cloudflare R2 access key
- `CLOUDFLARE_R2_ACCESS_KEY_ID` - Cloudflare R2 access key
- `CLOUDFLARE_R2_SECRET_ACCESS_KEY` - Cloudflare R2 secret key
- `CLOUDFLARE_R2_ACCOUNT_ID` - Cloudflare R2 account ID
- `CLOUDFLARE_R2_BUCKET_NAME` - Cloudflare R2 bucket name (may be missing locally)
- `DATABASE_URL` - Production database URL
- `SECRET_KEY` - Flask secret key

### Test-Specific Variables
- `TEST_DATABASE_URL` - Test database URL (created by setup script)
- `FLASK_ENV=testing` - Test environment flag
- `TESTING=true` - Testing flag

## Common Mistakes to Avoid

### ❌ DON'T DO THIS:
1. Try to access Vercel environment variables locally
2. Create `.env.test` files without copying real credentials
3. Assume environment variables exist when they don't
4. Write tests that expect external services to be available locally

### ✅ DO THIS INSTEAD:
1. Always check if environment variables are loaded: `python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('BLOB_READ_WRITE_TOKEN:', 'SET' if os.getenv('BLOB_READ_WRITE_TOKEN') else 'NOT SET')"`
2. Use mocks for external services in tests
3. Test application logic, not external service calls
4. Use local environment variables via dotenv

## Testing Strategy

### For Storage Tests:
- **Cloudflare R2**: Mock the `boto3` client calls
- **Database**: Use test database with `TEST_DATABASE_URL`
- **Authentication**: Use `authenticated_client` fixture

### Test Environment Setup:
```python
# Always use this pattern in tests
with test_app.app_context():
    # Test application logic here
    # Don't expect external service calls
    # Use mocks for external dependencies
```

## Verification Commands

### Check Environment Variables:
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('CLOUDFLARE_R2_ACCESS_KEY_ID:', 'SET' if os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID') else 'NOT SET'); print('CLOUDFLARE_R2_SECRET_ACCESS_KEY:', 'SET' if os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY') else 'NOT SET')"
```

### Check Test Environment:
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv('.env.test'); print('TEST_DATABASE_URL:', 'SET' if os.getenv('TEST_DATABASE_URL') else 'NOT SET')"
```

## File Structure
```
project_root/
├── .env                    # Local development environment variables
├── .env.test              # Test-specific environment variables (created by setup)
├── .vercel/               # Vercel project configuration
│   └── project.json       # Vercel project ID and settings
├── tests/
│   └── conftest.py        # Test configuration with load_dotenv()
└── app.py                 # Main application with load_dotenv()
```

## Troubleshooting

### If Tests Fail with Environment Variable Errors:
1. Check if `.env` file exists and has required variables
2. Verify `load_dotenv()` is called in test setup
3. Use mocks instead of real external services
4. Check if test database is properly configured

### If Production Deployments Fail:
1. Check Vercel environment variables are set
2. Verify all required variables are present in Vercel dashboard
3. Check Vercel project configuration in `.vercel/project.json`

## Remember This Pattern

**Every time I work on this project:**
1. **Environment variables are in Vercel for production**
2. **Environment variables are in `.env` file for local development**
3. **Tests should use local environment variables via dotenv**
4. **Tests should mock external services, not call them directly**
5. **Always verify environment variables are loaded before proceeding**

## Last Updated
- Date: 2025-08-25
- Context: After fixing recurring environment variable issues in test suite
- Status: All Vercel Blob tests now passing (8/8)
- Remaining: Cloudflare R2 tests need similar fixes
