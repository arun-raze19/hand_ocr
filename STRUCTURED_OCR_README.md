# Structured Document OCR Tool

A powerful Python tool for extracting structured data from handwritten and printed documents using Pydantic models and Groq's Llama 4 Scout vision model. Outputs comprehensive CSV files with vendor information, customer details, line items, and financial data.

## 🎯 Features

### **Comprehensive Data Extraction**
- **Vendor Information**: Company name, email, phone, full address details
- **Customer Information**: Name, contact details, billing address
- **Document Metadata**: Type, number, date, reference numbers
- **Line Items**: Item names, quantities, prices, totals, codes, categories
- **Financial Data**: Subtotals, tax information, total amounts, currency
- **Payment Details**: Methods, terms, due dates, balances

### **Advanced Processing**
- **Pydantic Data Validation**: Ensures data integrity and type safety
- **Dual CSV Output**: Summary view and detailed line-item view
- **Smart Data Parsing**: Automatic price, date, and phone number formatting
- **Error Handling**: Graceful handling of unclear or missing data
- **Batch Processing**: Process multiple documents simultaneously

### **Output Formats**
- **Summary CSV**: One row per document with primary line item
- **Detailed CSV**: One row per line item for comprehensive analysis
- **JSON**: Complete structured data for debugging and integration

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Key
Add your Groq API key to `.env`:
```
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Add Documents
Place your document images in `input_images/` folder:
- Invoices, receipts, bills
- Handwritten or printed documents
- Supported formats: JPG, PNG, BMP, TIFF

### 4. Run Structured OCR
```bash
python structured_ocr.py
```

## 📊 CSV Output Structure

### Summary CSV Fields
| Field | Description | Example |
|-------|-------------|---------|
| `document_type` | Type of document | invoice, receipt, bill |
| `document_number` | Document ID/number | INV-2024-001 |
| `document_date` | Document date | 2024-07-08 |
| `vendor_name` | Company/vendor name | ABC Company Ltd |
| `vendor_email` | Vendor email | billing@abc.com |
| `vendor_phone` | Vendor phone | (555) 123-4567 |
| `vendor_address` | Full vendor address | 123 Main St, Suite 100 |
| `customer_name` | Customer/bill-to name | John Smith |
| `customer_email` | Customer email | john@email.com |
| `customer_phone` | Customer phone | (555) 987-6543 |
| `item_name` | Primary item description | Professional Services |
| `quantity` | Item quantity | 5 |
| `unit_price` | Price per unit | 100.00 |
| `item_total_price` | Total for item | 500.00 |
| `subtotal` | Subtotal before tax | 500.00 |
| `tax_rate` | Tax percentage | 8.5 |
| `tax_amount` | Tax amount | 42.50 |
| `total_amount` | Final total | 542.50 |
| `currency` | Currency code | USD |
| `payment_method` | Payment type | Credit Card |
| `total_line_items` | Number of items | 3 |

### Detailed CSV Fields
Same as summary CSV plus:
- `line_item_number`: Sequential item number (1, 2, 3...)
- One row per line item for complete item analysis

## 🔧 Advanced Configuration

### Custom Models
Edit `structured_ocr.py` to use different models:
```python
self.vision_model = "meta-llama/llama-4-scout-17b-16e-instruct"
self.text_model = "llama-3.3-70b-versatile"
```

### Data Validation
The tool uses Pydantic models for robust data validation:
- **Automatic type conversion**: Strings to numbers, dates
- **Data cleaning**: Phone numbers, email addresses
- **Error handling**: Invalid data marked as null

### Output Customization
Modify `data_models.py` to add custom fields:
```python
class LineItem(BaseModel):
    custom_field: Optional[str] = Field(None, description="Custom field")
```

## 📁 File Structure

```
structured-ocr/
├── structured_ocr.py          # Main OCR script
├── data_models.py            # Pydantic data models
├── handwritten_ocr.py        # Original OCR tool
├── requirements.txt          # Dependencies
├── .env                     # API configuration
├── input_images/            # Place documents here
└── output/                  # Results saved here
    ├── structured_documents_TIMESTAMP.csv    # Summary CSV
    ├── detailed_line_items_TIMESTAMP.csv     # Detailed CSV
    └── structured_results_TIMESTAMP.json     # JSON data
```

## 💡 Tips for Best Results

### **Document Quality**
- Use high-resolution images (300+ DPI)
- Ensure good lighting and contrast
- Keep documents flat and unfolded
- Avoid shadows and glare

### **Document Types**
- **Invoices**: Excellent extraction of vendor, customer, and line items
- **Receipts**: Good for vendor info and purchase details
- **Bills**: Effective for service charges and customer data
- **Estimates**: Captures proposed work and pricing

### **Handwritten Documents**
- Clear, legible handwriting works best
- Dark ink on light paper
- Avoid cursive for numbers and critical data
- Print important information when possible

## 🔍 Example Output

For an invoice from "ABC Company" to "John Smith" with 3 line items:

**Summary CSV** (1 row):
```csv
document_type,vendor_name,customer_name,total_amount,total_line_items
invoice,ABC Company,John Smith,542.50,3
```

**Detailed CSV** (3 rows):
```csv
document_type,vendor_name,customer_name,item_name,quantity,unit_price,line_item_number
invoice,ABC Company,John Smith,Consulting,10,50.00,1
invoice,ABC Company,John Smith,Materials,1,200.00,2
invoice,ABC Company,John Smith,Labor,5,60.00,3
```

## 🛠️ Troubleshooting

### Common Issues

1. **"No structured data extracted"**
   - Check image quality and lighting
   - Ensure document contains readable text
   - Try preprocessing the image externally

2. **"Missing vendor/customer information"**
   - Verify contact details are clearly visible
   - Check for handwritten vs. printed text clarity
   - Ensure addresses are complete

3. **"Incorrect price parsing"**
   - Verify currency symbols are clear
   - Check for decimal point visibility
   - Ensure numbers aren't obscured

### Performance Tips

- **Batch processing**: Process multiple documents at once
- **Image optimization**: Resize very large images before processing
- **API limits**: Monitor your Groq API usage and rate limits

## 🔄 Migration from Basic OCR

If upgrading from `handwritten_ocr.py`:

1. **Install new dependencies**: `pip install pydantic pandas`
2. **Use new script**: `python structured_ocr.py`
3. **Check CSV outputs**: More structured than text files
4. **Update integrations**: Use CSV data instead of raw text

## 📈 Integration Examples

### **Excel Analysis**
```python
import pandas as pd
df = pd.read_csv('output/structured_documents_TIMESTAMP.csv')
total_revenue = df['total_amount'].sum()
```

### **Database Import**
```python
import sqlite3
df = pd.read_csv('output/detailed_line_items_TIMESTAMP.csv')
df.to_sql('invoices', conn, if_exists='append')
```

### **Business Intelligence**
- Import CSV into Power BI, Tableau, or Excel
- Analyze vendor performance and customer patterns
- Track revenue and payment trends

## 🎉 Success!

Your structured OCR tool is now ready to extract comprehensive business data from documents with high accuracy and structured output perfect for analysis and integration!
