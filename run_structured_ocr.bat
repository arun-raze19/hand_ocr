@echo off
echo ========================================
echo   Structured Document OCR Tool
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
echo Starting structured OCR processing...
echo This will extract:
echo - Vendor information (name, email, phone, address)
echo - Customer details (name, contact info)
echo - Line items (description, quantity, price)
echo - Financial data (subtotal, tax, total)
echo - Payment information
echo.
python structured_ocr.py

echo.
echo Processing complete!
echo Check the 'output' folder for CSV files:
echo - structured_documents_*.csv (summary view)
echo - detailed_line_items_*.csv (detailed view)
echo.
pause
