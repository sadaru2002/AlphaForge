@echo off
echo ========================================
echo AlphaForge OANDA Backtesting
echo ========================================
echo.

REM Check if OANDA_API_KEY is set
if "%OANDA_API_KEY%"=="" (
    echo ERROR: OANDA_API_KEY not set!
    echo.
    echo Please set your OANDA API key first:
    echo   $env:OANDA_API_KEY = 'your-api-key-here'
    echo.
    pause
    exit /b 1
)

echo API Key: Set ✓
echo.

REM Navigate to backend directory
cd /d "%~dp0backend"

echo Running backtest...
echo.

python backtest_oanda.py

echo.
echo ========================================
echo Backtest Complete!
echo ========================================
pause
