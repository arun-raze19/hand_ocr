#!/usr/bin/env pwsh

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Handwritten OCR Processing Tool" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (Test-Path "tcsenv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "tcsenv\Scripts\Activate.ps1"
} elseif (Test-Path "tcsenv\Scripts\activate.bat") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "tcsenv\Scripts\activate.bat"
} else {
    Write-Host "Warning: Virtual environment not found at tcsenv\" -ForegroundColor Yellow
    Write-Host "Using system Python..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Checking setup..." -ForegroundColor Green
python test_setup.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Setup validation failed. Please fix the issues above." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Starting OCR processing..." -ForegroundColor Green
Write-Host ""
python handwritten_ocr.py

Write-Host ""
Write-Host "Processing complete!" -ForegroundColor Green
Write-Host "Check the 'output' folder for results." -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit"
