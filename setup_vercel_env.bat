@echo off
echo 🔧 Setting up Vercel Environment Variables...
echo.

echo 📋 Adding DATABASE_URL...
vercel env add DATABASE_URL production
echo.

echo 📋 Adding BLOB_READ_WRITE_TOKEN...
vercel env add BLOB_READ_WRITE_TOKEN production
echo.

echo 📋 Adding SECRET_KEY...
vercel env add SECRET_KEY production
echo.

echo 📋 Adding TOTP_ENCRYPTION_KEY...
vercel env add TOTP_ENCRYPTION_KEY production
echo.

echo 📋 Adding BCRYPT_ROUNDS...
vercel env add BCRYPT_ROUNDS production
echo.

echo 📋 Adding FLASK_ENV...
vercel env add FLASK_ENV production
echo.

echo ✅ Environment variables added!
echo.
echo 🚀 Now redeploy with: vercel --prod
echo.
pause
