# AlphaForge OANDA Backtesting Script
# Run this in PowerShell

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "AlphaForge OANDA Backtesting" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if OANDA_API_KEY is set
if (-not $env:OANDA_API_KEY) {
    Write-Host "❌ ERROR: OANDA_API_KEY not set!`n" -ForegroundColor Red
    Write-Host "Please set your OANDA API key first:" -ForegroundColor Yellow
    Write-Host "  `$env:OANDA_API_KEY = 'your-api-key-here'`n" -ForegroundColor White
    
    # Prompt for API key
    $apiKey = Read-Host "Enter your OANDA API key (or press Enter to exit)"
    
    if ($apiKey) {
        $env:OANDA_API_KEY = $apiKey
        Write-Host "`n✅ API Key set for this session!`n" -ForegroundColor Green
    } else {
        Write-Host "`nExiting...`n" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "✅ API Key: Set" -ForegroundColor Green
}

# Navigate to backend directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$scriptDir\backend"

Write-Host "`n🚀 Running backtest...`n" -ForegroundColor Cyan

# Run the backtest
python backtest_oanda.py

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Backtest Complete!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

# Ask if user wants to run again
$again = Read-Host "Run another backtest? (y/n)"
if ($again -eq "y" -or $again -eq "Y") {
    & $MyInvocation.MyCommand.Path
}
