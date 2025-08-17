# PowerShell 7 Setup Script
# This script helps configure PowerShell 7 for better compatibility

Write-Host "Setting up PowerShell 7 for better compatibility..." -ForegroundColor Green

# Add PowerShell 7 to PATH for current session
$env:PATH += ";C:\Program Files\PowerShell\7"

# Test if pwsh is now available
try {
    $version = & "C:\Program Files\PowerShell\7\pwsh.exe" -Version
    Write-Host "✅ PowerShell 7 is available: $version" -ForegroundColor Green

    # Test git functionality
    Write-Host "Testing git functionality..." -ForegroundColor Yellow
    & "C:\Program Files\PowerShell\7\pwsh.exe" -Command "git --version"

    Write-Host "`n🎉 PowerShell 7 is ready to use!" -ForegroundColor Green
    Write-Host "To use it in Cursor:" -ForegroundColor Cyan
    Write-Host "1. Open Cursor settings" -ForegroundColor White
    Write-Host "2. Search for 'terminal.integrated.shell.windows'" -ForegroundColor White
    Write-Host "3. Set it to: C:\Program Files\PowerShell\7\pwsh.exe" -ForegroundColor White
    Write-Host "`nOr run: pwsh" -ForegroundColor Yellow

} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
