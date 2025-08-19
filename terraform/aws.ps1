#!/usr/bin/env pwsh
<#
.SYNOPSIS
    AWS CLI wrapper script for AFROTC 2FA infrastructure

.DESCRIPTION
    This script provides easy access to AWS CLI commands with proper PATH handling.
    It automatically finds the AWS CLI installation and runs the specified command.

.PARAMETER Command
    The AWS CLI command to run (sts, ses, configure, etc.)

.PARAMETER Arguments
    Additional arguments to pass to AWS CLI

.EXAMPLE
    .\aws.ps1 configure
    .\aws.ps1 sts get-caller-identity
    .\aws.ps1 ses get-send-quota
#>

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$Command,

    [Parameter(Mandatory=$false, Position=1, ValueFromRemainingArguments=$true)]
    [string[]]$Arguments
)

# Find AWS CLI installation
$awsPaths = @(
    "aws",
    "C:\Program Files\Amazon\AWSCLIV2\aws.exe",
    "C:\Program Files (x86)\Amazon\AWSCLIV2\aws.exe",
    "C:\aws\aws.exe"
)

$awsExe = $null
foreach ($path in $awsPaths) {
    if (Get-Command $path -ErrorAction SilentlyContinue) {
        $awsExe = $path
        break
    }
}

if (-not $awsExe) {
    Write-Host "❌ AWS CLI not found. Please install AWS CLI first." -ForegroundColor Red
    Write-Host "Run: winget install -e --id Amazon.AWSCLI" -ForegroundColor Yellow
    exit 1
}

# Build command
$fullCommand = @($awsExe, $Command) + $Arguments

# Execute AWS CLI
Write-Host "🔧 Running: $($fullCommand -join ' ')" -ForegroundColor Cyan
Write-Host ""

& $awsExe $Command @Arguments

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ AWS CLI command failed with exit code: $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}

