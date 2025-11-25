# AlphaForge August 2024 Multi-Instrument Backtest
# Run this in PowerShell

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "AlphaForge August 2024 Backtest" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if OANDA_API_KEY is set
if (-not $env:OANDA_API_KEY) {
    Write-Host "❌ ERROR: OANDA_API_KEY not set!`n" -ForegroundColor Red
    Write-Host "Please set your OANDA API key first:" -ForegroundColor Yellow
    Write-Host "  `$env:OANDA_API_KEY = 'your-api-key-here'`n" -ForegroundColor White
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

Write-Host "`n🚀 Running monthly backtest (Aug 2024) for GBP_USD, XAU_USD, USD_JPY...`n" -ForegroundColor Cyan

# Run the month runner
python .\backtest_month_runner.py

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Backtest Complete!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan
