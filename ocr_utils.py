"""
Utility functions for handwritten OCR processing
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Tuple
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import numpy as np

class ImageProcessor:
    """Advanced image processing utilities for OCR"""
    
    @staticmethod
    def enhance_handwriting(image: Image.Image) -> Image.Image:
        """
        Apply specific enhancements for handwritten text recognition
        """
        # Convert to grayscale if not already
        if image.mode != 'L':
            image = image.convert('L')
        
        # Auto-contrast to improve text visibility
        image = ImageOps.autocontrast(image, cutoff=2)
        
        # Enhance contrast specifically for handwriting
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.8)
        
        # Sharpen to make text edges clearer
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.2)
        
        # Apply unsharp mask for better text definition
        image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
        
        return image.convert('RGB')
    
    @staticmethod
    def detect_text_regions(image: Image.Image) -> List[Tuple[int, int, int, int]]:
        """
        Detect potential text regions in the image
        Returns list of (x, y, width, height) tuples
        """
        # Convert to numpy array for processing
        img_array = np.array(image.convert('L'))
        
        # Simple text region detection based on pixel density
        # This is a basic implementation - could be enhanced with OpenCV
        height, width = img_array.shape
        
        # Divide image into grid and analyze each cell
        grid_size = 50
        text_regions = []
        
        for y in range(0, height - grid_size, grid_size // 2):
            for x in range(0, width - grid_size, grid_size // 2):
                region = img_array[y:y+grid_size, x:x+grid_size]
                
                # Calculate variance (text regions have higher variance)
                variance = np.var(region)
                
                # If variance is above threshold, likely contains text
                if variance > 500:  # Threshold may need adjustment
                    text_regions.append((x, y, grid_size, grid_size))
        
        return text_regions
    
    @staticmethod
    def adaptive_split(image: Image.Image, min_sections: int = 2, max_sections: int = 6) -> List[Image.Image]:
        """
        Adaptively split image based on content and size
        """
        width, height = image.size
        
        # Determine optimal number of sections based on image size
        if height < 800:
            sections = min_sections
        elif height < 1600:
            sections = 3
        elif height < 2400:
            sections = 4
        else:
            sections = max_sections
        
        # Split with adaptive overlap
        overlap = 0.15 if sections <= 3 else 0.2
        section_height = height // sections
        overlap_height = int(section_height * overlap)
        
        sections_list = []
        for i in range(sections):
            upper = max(i * section_height - overlap_height, 0)
            lower = min((i + 1) * section_height + overlap_height, height)
            section = image.crop((0, upper, width, lower))
            sections_list.append(section)
        
        return sections_list

class ResultsManager:
    """Manage OCR results and output formatting"""
    
    @staticmethod
    def format_extracted_text(text: str, filename: str) -> str:
        """Format extracted text with metadata"""
        from datetime import datetime
        formatted = f"""
HANDWRITTEN OCR EXTRACTION
==========================
Source File: {filename}
Extraction Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
==========================

{text}

==========================
End of Extraction
"""
        return formatted.strip()
    
    @staticmethod
    def create_summary_report(results: List[Dict]) -> str:
        """Create a summary report of all processed files"""
        from datetime import datetime
        total_files = len(results)
        successful = sum(1 for r in results if r["status"] == "success")
        failed = total_files - successful
        
        report = f"""
HANDWRITTEN OCR PROCESSING REPORT
=================================

Processing Summary:
- Total Files: {total_files}
- Successfully Processed: {successful}
- Failed: {failed}
- Success Rate: {(successful/total_files*100):.1f}%

File Details:
"""
        
        for result in results:
            status_icon = "✅" if result["status"] == "success" else "❌"
            report += f"\n{status_icon} {result['filename']}"
            if result["status"] == "success":
                text_length = len(result.get("extracted_text", ""))
                report += f" ({text_length} characters extracted)"
            else:
                report += f" (Error: {result.get('error', 'Unknown error')})"
        
        report += f"\n\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return report
    
    @staticmethod
    def export_to_formats(results: List[Dict], output_dir: Path):
        """Export results to multiple formats"""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create consolidated text file
        consolidated_file = output_dir / f"all_extracted_text_{timestamp}.txt"
        with open(consolidated_file, 'w', encoding='utf-8') as f:
            for result in results:
                if result["status"] == "success" and result.get("extracted_text"):
                    f.write(f"\n{'='*60}\n")
                    f.write(f"FILE: {result['filename']}\n")
                    f.write(f"{'='*60}\n\n")
                    f.write(result["extracted_text"])
                    f.write("\n\n")
        
        # Create CSV summary (if needed for analysis)
        csv_file = output_dir / f"processing_summary_{timestamp}.csv"
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write("filename,status,text_length,processed_at\n")
            for result in results:
                text_length = len(result.get("extracted_text", "")) if result["status"] == "success" else 0
                f.write(f'"{result["filename"]}",{result["status"]},{text_length},"{result["processed_at"]}"\n')
        
        return consolidated_file, csv_file

def validate_image_file(file_path: Path) -> bool:
    """Validate if file is a supported image format"""
    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    
    if file_path.suffix.lower() not in supported_formats:
        return False
    
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False

def get_image_info(file_path: Path) -> Dict:
    """Get detailed information about an image file"""
    try:
        with Image.open(file_path) as img:
            return {
                "filename": file_path.name,
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "file_size": file_path.stat().st_size,
                "valid": True
            }
    except Exception as e:
        return {
            "filename": file_path.name,
            "error": str(e),
            "valid": False
        }

def print_processing_stats(results: List[Dict]):
    """Print detailed processing statistics"""
    if not results:
        print("No results to display")
        return
    
    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "error"]
    
    print(f"\n📊 PROCESSING STATISTICS")
    print(f"{'='*50}")
    print(f"Total Files Processed: {len(results)}")
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"Success Rate: {len(successful)/len(results)*100:.1f}%")
    
    if successful:
        text_lengths = [len(r.get("extracted_text", "")) for r in successful]
        avg_length = sum(text_lengths) / len(text_lengths)
        print(f"\nText Extraction Stats:")
        print(f"Average text length: {avg_length:.0f} characters")
        print(f"Total text extracted: {sum(text_lengths):,} characters")
    
    if failed:
        print(f"\n❌ Failed Files:")
        for result in failed:
            print(f"   • {result['filename']}: {result.get('error', 'Unknown error')}")
