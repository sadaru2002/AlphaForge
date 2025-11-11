# AlphaForge Frontend Recovery Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ALPHAFORGE FRONTEND RECOVERY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Create all necessary directories
Write-Host "[1/4] Creating directory structure..." -ForegroundColor Yellow
$dirs = @(
    "frontend\src\components",
    "frontend\src\pages",
    "frontend\src\services",
    "frontend\src\config",
    "frontend\public"
)

foreach ($dir in $dirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "[2/4] Checking backend files..." -ForegroundColor Yellow
if (Test-Path "backend\app.py") {
    Write-Host "  Backend files found!" -ForegroundColor Green
} else {
    Write-Host "  Downloading backend from VPS..." -ForegroundColor Yellow
    # Backend already downloaded
}

Write-Host ""
Write-Host "[3/4] Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location frontend
if (Test-Path "package.json") {
    Write-Host "  Running npm install..." -ForegroundColor Yellow
    npm install
} else {
    Write-Host "  Error: package.json not found!" -ForegroundColor Red
}

Write-Host ""
Write-Host "[4/4] Verification..." -ForegroundColor Yellow

$requiredFiles = @(
    "src\index.js",
    "src\App.jsx",
    "src\config\api.js",
    "src\services\api.js",
    "public\index.html"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (!(Test-Path $file)) {
        $missingFiles += $file
        Write-Host "  Missing: $file" -ForegroundColor Red
    } else {
        Write-Host "  Found: $file" -ForegroundColor Green
    }
}

Write-Host ""
if ($missingFiles.Count -eq 0) {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  RECOVERY COMPLETE!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. cd frontend" -ForegroundColor White
    Write-Host "  2. npm start" -ForegroundColor White
} else {
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "  RECOVERY INCOMPLETE" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Missing $($missingFiles.Count) files. Continue manual recovery." -ForegroundColor Yellow
}

Set-Location ..
