import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from PIL import Image, ImageEnhance, ImageFilter
from langchain_groq import ChatGroq
import base64
import io
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class HandwrittenOCR:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.vision_model = "meta-llama/llama-4-maverick-17b-128e-instruct"
        self.text_model = "llama-3.3-70b-versatile"
        
        # Create directories
        self.input_dir = Path("input_images")
        self.output_dir = Path("output")
        self.input_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        print(f"✅ Initialized HandwrittenOCR")
        print(f"📁 Input directory: {self.input_dir.absolute()}")
        print(f"📁 Output directory: {self.output_dir.absolute()}")

    def encode_image_pil(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        buffered = io.BytesIO()
        image = image.convert("RGB")
        image.save(buffered, format="JPEG", quality=95)
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Enhance image for better OCR results"""
        # Convert to grayscale for better contrast
        if image.mode != 'L':
            image = image.convert('L')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        
        # Apply slight blur to reduce noise
        image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        return image.convert('RGB')

    def split_image_into_sections(self, image: Image.Image, sections: int = 4, overlap: float = 0.15) -> List[Image.Image]:
        """Split image into overlapping horizontal sections for better processing"""
        width, height = image.size
        section_height = height // sections
        overlap_height = int(section_height * overlap)
        
        sections_list = []
        for i in range(sections):
            upper = max(i * section_height - overlap_height, 0)
            lower = min((i + 1) * section_height + overlap_height, height)
            section = image.crop((0, upper, width, lower))
            sections_list.append(section)
        
        return sections_list

    def extract_handwritten_text(self, image: Image.Image) -> str:
        """Extract handwritten text from image using Groq Vision API"""
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
                            "You are an expert in reading handwritten text. Please carefully analyze this image and extract ALL handwritten text you can see. "
                            "Pay special attention to:\n"
                            "1. Cursive and script handwriting\n"
                            "2. Print handwriting\n"
                            "3. Numbers and dates\n"
                            "4. Signatures and names\n"
                            "5. Any annotations or notes\n\n"
                            "Please transcribe the text exactly as written, maintaining the original structure and line breaks. "
                            "If text is unclear, indicate with [unclear] but still provide your best interpretation. "
                            "If you see printed text mixed with handwritten text, clearly distinguish between them."
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
            print(f"❌ Error in OCR processing: {str(e)}")
            return f"Error processing image: {str(e)}"

    def consolidate_text_sections(self, text_sections: List[str]) -> str:
        """Consolidate overlapping text sections into coherent document"""
        if not text_sections:
            return ""
        
        if len(text_sections) == 1:
            return text_sections[0]

        groq_llm = ChatGroq(
            groq_api_key=self.groq_api_key,
            model_name=self.text_model,
            temperature=0
        )

        combined_text = "\n\n--- SECTION BREAK ---\n\n".join(text_sections)

        messages = [
            {
                "role": "user",
                "content": (
                    "You are provided with multiple text extractions from overlapping sections of a handwritten document. "
                    "Some sections may contain duplicate or partially repeated content due to overlaps.\n\n"
                    "Your task is to:\n"
                    "1. Identify and remove duplicate content while preserving the complete text\n"
                    "2. Maintain the original structure and flow of the handwritten document\n"
                    "3. Resolve any conflicts by choosing the most complete/accurate version\n"
                    "4. Preserve line breaks and paragraph structure\n"
                    "5. Keep any formatting indicators like [unclear] if present\n\n"
                    "Return only the consolidated, clean text without any additional comments.\n\n"
                    "Text sections to consolidate:\n\n" + combined_text
                )
            }
        ]

        try:
            response = groq_llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            print(f"❌ Error in text consolidation: {str(e)}")
            return "\n\n".join(text_sections)  # Fallback to simple join

    def process_single_image(self, image_path: Path) -> Dict:
        """Process a single image and return results"""
        print(f"\n📄 Processing: {image_path.name}")
        
        try:
            # Load and preprocess image
            image = Image.open(image_path)
            print(f"   📏 Original size: {image.size}")
            
            # Preprocess for better OCR
            processed_image = self.preprocess_image(image)
            
            # Split into sections for better processing
            sections = self.split_image_into_sections(processed_image, sections=3, overlap=0.2)
            print(f"   ✂️  Split into {len(sections)} sections")
            
            # Extract text from each section
            text_sections = []
            for i, section in enumerate(sections, 1):
                print(f"   🔍 Processing section {i}/{len(sections)}...")
                section_text = self.extract_handwritten_text(section)
                text_sections.append(section_text)
            
            # Consolidate all sections
            print("   🔗 Consolidating sections...")
            final_text = self.consolidate_text_sections(text_sections)
            
            result = {
                "filename": image_path.name,
                "processed_at": datetime.now().isoformat(),
                "image_size": image.size,
                "sections_processed": len(sections),
                "extracted_text": final_text,
                "status": "success"
            }
            
            print(f"   ✅ Successfully processed {image_path.name}")
            return result
            
        except Exception as e:
            error_result = {
                "filename": image_path.name,
                "processed_at": datetime.now().isoformat(),
                "error": str(e),
                "status": "error"
            }
            print(f"   ❌ Error processing {image_path.name}: {str(e)}")
            return error_result

    def process_all_images(self) -> List[Dict]:
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

    def save_results(self, results: List[Dict]):
        """Save processing results to files"""
        if not results:
            print("❌ No results to save")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_file = self.output_dir / f"ocr_results_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Save text files for each successful extraction
        text_dir = self.output_dir / f"extracted_text_{timestamp}"
        text_dir.mkdir(exist_ok=True)
        
        for result in results:
            if result["status"] == "success" and result.get("extracted_text"):
                filename = Path(result["filename"]).stem
                text_file = text_dir / f"{filename}_extracted.txt"
                with open(text_file, 'w', encoding='utf-8') as f:
                    f.write(f"Extracted from: {result['filename']}\n")
                    f.write(f"Processed at: {result['processed_at']}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(result["extracted_text"])
        
        print(f"\n💾 Results saved:")
        print(f"   📄 JSON summary: {json_file}")
        print(f"   📁 Text files: {text_dir}")

def main():
    """Main function to run the OCR tool"""
    print("🚀 Starting Handwritten OCR Tool")
    print("=" * 50)
    
    try:
        # Initialize OCR tool
        ocr_tool = HandwrittenOCR()
        
        # Process all images
        results = ocr_tool.process_all_images()
        
        # Save results
        ocr_tool.save_results(results)
        
        # Print summary
        successful = sum(1 for r in results if r["status"] == "success")
        failed = len(results) - successful
        
        print(f"\n📊 Processing Summary:")
        print(f"   ✅ Successful: {successful}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📁 Total processed: {len(results)}")
        
        if successful > 0:
            print(f"\n🎉 OCR processing completed successfully!")
            print(f"   Check the 'output' folder for results.")
        
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")

if __name__ == "__main__":
    main()
