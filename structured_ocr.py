"""
Enhanced Structured OCR Tool with Pydantic models and CSV output
"""

import os
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from PIL import Image, ImageEnhance, ImageFilter
from langchain_groq import ChatGroq
import base64
import io
import pandas as pd
from dotenv import load_dotenv

from data_models import StructuredDocument, ContactInfo, LineItem, TaxInfo, PaymentInfo, DocumentInfo

# Load environment variables
load_dotenv()


class StructuredDocumentOCR:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.vision_model = "meta-llama/llama-4-scout-17b-16e-instruct"
        self.text_model = "llama-3.3-70b-versatile"
        
        # Create directories
        self.input_dir = Path("input_images")
        self.output_dir = Path("output")
        self.input_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        print(f"✅ Initialized Structured Document OCR")
        print(f"📁 Input directory: {self.input_dir.absolute()}")
        print(f"📁 Output directory: {self.output_dir.absolute()}")

    def encode_image_pil(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        buffered = io.BytesIO()
        image = image.convert("RGB")
        image.save(buffered, format="JPEG", quality=95)
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Enhanced image preprocessing for document OCR"""
        # Convert to grayscale for better contrast
        if image.mode != 'L':
            image = image.convert('L')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.8)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.2)
        
        # Apply slight blur to reduce noise
        image = image.filter(ImageFilter.GaussianBlur(radius=0.3))
        
        return image.convert('RGB')

    def extract_raw_text(self, image: Image.Image) -> str:
        """Extract raw text from image using vision model"""
        groq_llm = ChatGroq(
            groq_api_key=self.groq_api_key,
            model_name=self.vision_model,
            temperature=0
        )

        image_data_url = f"data:image/jpeg;base64,{self.encode_image_pil(image)}"

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text": (
                            "You are an expert OCR system. Extract ALL text from this document image with perfect accuracy. "
                            "Include:\n"
                            "- All printed text\n"
                            "- All handwritten text\n"
                            "- Numbers, dates, prices\n"
                            "- Company names, addresses\n"
                            "- Email addresses, phone numbers\n"
                            "- Item descriptions and quantities\n"
                            "- Any signatures or notes\n\n"
                            "Preserve the original layout and structure. "
                            "If text is unclear, provide your best interpretation."
                        )
                    },
                    {"type": "image_url", "image_url": {"url": image_data_url}}
                ]
            }
        ]

        try:
            response = groq_llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            print(f"❌ Error in raw text extraction: {str(e)}")
            return f"Error processing image: {str(e)}"

    def extract_structured_data(self, raw_text: str, filename: str) -> StructuredDocument:
        """Extract structured data from raw text using LLM"""
        groq_llm = ChatGroq(
            groq_api_key=self.groq_api_key,
            model_name=self.text_model,
            temperature=0
        )

        prompt = f"""
You are an expert data extraction system. Extract structured information from this document text and return it as a JSON object.

DOCUMENT TEXT:
{raw_text}

Extract the following information and return as valid JSON:

{{
  "document_info": {{
    "document_type": "invoice/receipt/bill/estimate/etc",
    "document_number": "invoice/receipt number",
    "document_date": "YYYY-MM-DD format",
    "reference_number": "PO or reference number"
  }},
  "vendor": {{
    "name": "company/vendor name",
    "email": "vendor email",
    "phone": "vendor phone",
    "address": "full vendor address",
    "city": "vendor city",
    "state": "vendor state",
    "postal_code": "vendor zip/postal code",
    "country": "vendor country"
  }},
  "customer": {{
    "name": "customer/bill-to name",
    "email": "customer email",
    "phone": "customer phone", 
    "address": "customer address",
    "city": "customer city",
    "state": "customer state",
    "postal_code": "customer zip/postal code",
    "country": "customer country"
  }},
  "line_items": [
    {{
      "item_name": "item description",
      "quantity": number,
      "unit_price": number,
      "total_price": number,
      "item_code": "product code/SKU",
      "category": "item category"
    }}
  ],
  "subtotal": number,
  "tax_info": {{
    "tax_rate": percentage,
    "tax_amount": number,
    "tax_type": "VAT/GST/Sales Tax/etc"
  }},
  "total_amount": number,
  "payment_info": {{
    "payment_method": "cash/card/check/etc",
    "payment_terms": "payment terms",
    "due_date": "YYYY-MM-DD",
    "paid_amount": number,
    "balance_due": number
  }},
  "notes": "any additional notes",
  "currency": "USD/EUR/etc"
}}

IMPORTANT:
- Return ONLY valid JSON, no additional text
- Use null for missing values
- Extract ALL line items found
- Be precise with numbers and dates
- Include partial information even if incomplete
- Look for handwritten additions or modifications
"""

        try:
            response = groq_llm.invoke([{"role": "user", "content": prompt}])
            json_text = response.content.strip()
            
            # Clean up the response to ensure it's valid JSON
            if json_text.startswith('```json'):
                json_text = json_text[7:]
            if json_text.endswith('```'):
                json_text = json_text[:-3]
            
            # Parse JSON and create structured document
            data = json.loads(json_text)
            
            # Create Pydantic model
            structured_doc = StructuredDocument(
                document_info=DocumentInfo(**data.get('document_info', {})),
                vendor=ContactInfo(**data.get('vendor', {})),
                customer=ContactInfo(**data.get('customer', {})),
                line_items=[LineItem(**item) for item in data.get('line_items', [])],
                subtotal=data.get('subtotal'),
                tax_info=TaxInfo(**data.get('tax_info', {})),
                total_amount=data.get('total_amount'),
                payment_info=PaymentInfo(**data.get('payment_info', {})),
                notes=data.get('notes'),
                currency=data.get('currency', 'USD'),
                source_filename=filename,
                processed_at=datetime.now()
            )
            
            return structured_doc
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {str(e)}")
            print(f"Raw response: {response.content[:500]}...")
            # Return empty structured document with error info
            return StructuredDocument(
                source_filename=filename,
                notes=f"JSON parsing error: {str(e)}",
                processed_at=datetime.now()
            )
        except Exception as e:
            print(f"❌ Error in structured extraction: {str(e)}")
            return StructuredDocument(
                source_filename=filename,
                notes=f"Extraction error: {str(e)}",
                processed_at=datetime.now()
            )

    def process_single_image(self, image_path: Path) -> StructuredDocument:
        """Process a single image and return structured data"""
        print(f"\n📄 Processing: {image_path.name}")
        
        try:
            # Load and preprocess image
            image = Image.open(image_path)
            print(f"   📏 Original size: {image.size}")
            
            # Preprocess for better OCR
            processed_image = self.preprocess_image(image)
            
            # Extract raw text
            print("   🔍 Extracting raw text...")
            raw_text = self.extract_raw_text(processed_image)
            
            # Extract structured data
            print("   🏗️  Extracting structured data...")
            structured_doc = self.extract_structured_data(raw_text, image_path.name)
            
            print(f"   ✅ Successfully processed {image_path.name}")
            return structured_doc
            
        except Exception as e:
            print(f"   ❌ Error processing {image_path.name}: {str(e)}")
            return StructuredDocument(
                source_filename=image_path.name,
                notes=f"Processing error: {str(e)}",
                processed_at=datetime.now()
            )

    def process_all_images(self) -> List[StructuredDocument]:
        """Process all images in the input directory"""
        # Supported image formats
        supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        
        # Find all image files
        image_files = [
            f for f in self.input_dir.iterdir() 
            if f.is_file() and f.suffix.lower() in supported_formats
        ]
        
        if not image_files:
            print(f"❌ No image files found in {self.input_dir}")
            print(f"   Supported formats: {', '.join(supported_formats)}")
            return []
        
        print(f"🔍 Found {len(image_files)} image(s) to process")
        
        results = []
        for image_file in image_files:
            result = self.process_single_image(image_file)
            results.append(result)
        
        return results

    def save_to_csv(self, documents: List[StructuredDocument]):
        """Save structured documents to a single comprehensive CSV format"""
        if not documents:
            print("❌ No documents to save")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = self.output_dir / f"structured_documents_{timestamp}.csv"

        # Combine all line items from all documents
        all_items = []
        for doc in documents:
            if doc.line_items:
                # If document has line items, create one row per item
                all_items.extend(doc.to_line_items_list())
            else:
                # If no line items, create one row for the document
                all_items.append(doc.to_flat_dict())

        # Create DataFrame and save
        df = pd.DataFrame(all_items)
        df.to_csv(csv_file, index=False, encoding='utf-8')

        print(f"💾 Combined CSV saved: {csv_file}")
        return csv_file

    def save_results(self, documents: List[StructuredDocument]):
        """Save all results in multiple formats"""
        if not documents:
            print("❌ No results to save")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save JSON for debugging
        json_file = self.output_dir / f"structured_results_{timestamp}.json"
        json_data = [doc.model_dump() for doc in documents]
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False, default=str)

        # Save single combined CSV file
        csv_file = self.save_to_csv(documents)

        print(f"\n💾 Results saved:")
        print(f"   📄 JSON data: {json_file}")
        print(f"   📊 Combined CSV: {csv_file}")


def main():
    """Main function to run the structured OCR tool"""
    print("🚀 Starting Structured Document OCR Tool")
    print("=" * 60)
    
    try:
        # Initialize OCR tool
        ocr_tool = StructuredDocumentOCR()
        
        # Process all images
        documents = ocr_tool.process_all_images()
        
        # Save results
        ocr_tool.save_results(documents)
        
        # Print summary
        successful = sum(1 for doc in documents if doc.source_filename and not doc.notes.startswith("Error"))
        failed = len(documents) - successful
        
        print(f"\n📊 Processing Summary:")
        print(f"   ✅ Successful: {successful}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📁 Total processed: {len(documents)}")
        
        if successful > 0:
            print(f"\n🎉 Structured OCR processing completed!")
            print(f"   📊 Check CSV files in the 'output' folder for structured data.")
        
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")


if __name__ == "__main__":
    main()
