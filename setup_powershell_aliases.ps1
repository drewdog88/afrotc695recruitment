# PowerShell Development Aliases and Functions
# Add these to your PowerShell profile for better development experience

# Git shortcuts
Set-Alias -Name gs -Value git-status
Set-Alias -Name ga -Value git-add
Set-Alias -Name gc -Value git-commit
Set-Alias -Name gp -Value git-push
Set-Alias -Name gl -Value git-log

# Function to quickly switch to PowerShell 7
function Use-PS7 {
    & "C:\Program Files\PowerShell\7\pwsh.exe"
}

# Function to check git status with colors
function git-status {
    git status
}

# Function to add all changes and commit
function git-quick-commit {
    param([string]$Message = "Quick commit")
    git add .
    git commit -m $Message
}

# Function to push with status
function git-push-status {
    git push
    Write-Host "✅ Push completed successfully!" -ForegroundColor Green
}

# Function to check if we're in a git repo
function Test-GitRepo {
    if (Test-Path .git) {
        Write-Host "✅ In a git repository" -ForegroundColor Green
        git status --porcelain
    } else {
        Write-Host "❌ Not in a git repository" -ForegroundColor Red
    }
}

# Function to clean up temporary files
function Clear-TempFiles {
    Get-ChildItem -Path . -Include "*.tmp", "*.log", "*.cache" -Recurse | Remove-Item -Force
    Write-Host "🧹 Temporary files cleaned up" -ForegroundColor Green
}

# Function to check Python environment
function Test-PythonEnv {
    Write-Host "Python version:" -ForegroundColor Cyan
    python --version
    Write-Host "`nPip packages:" -ForegroundColor Cyan
    pip list
}

Write-Host "🚀 PowerShell development aliases loaded!" -ForegroundColor Green
Write-Host "Available commands:" -ForegroundColor Yellow
Write-Host "  gs - git status" -ForegroundColor White
Write-Host "  ga - git add" -ForegroundColor White
Write-Host "  gc - git commit" -ForegroundColor White
Write-Host "  gp - git push" -ForegroundColor White
Write-Host "  Use-PS7 - switch to PowerShell 7" -ForegroundColor White
Write-Host "  Test-GitRepo - check git repository status" -ForegroundColor White
Write-Host "  Clear-TempFiles - clean up temporary files" -ForegroundColor White
Write-Host "  Test-PythonEnv - check Python environment" -ForegroundColor White
