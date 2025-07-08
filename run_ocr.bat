@echo off
echo ========================================
echo    Handwritten OCR Processing Tool
echo ========================================
echo.

REM Check if virtual environment exists
if exist "tcsenv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call tcsenv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found at tcsenv\
    echo Using system Python...
)

echo.
echo Checking setup...
python test_setup.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Setup validation failed. Please fix the issues above.
    pause
    exit /b 1
)

echo.
echo Starting OCR processing...
echo.
python handwritten_ocr.py

echo.
echo Processing complete!
echo Check the 'output' folder for results.
echo.
pause
