# Handwritten OCR Tool

A powerful Python tool for extracting text from handwritten documents using the Llama 3.2 Vision model via Groq API.

## Features

- **Advanced Handwriting Recognition**: Specialized prompts for cursive, print, and mixed handwriting
- **Image Preprocessing**: Automatic contrast enhancement, sharpening, and noise reduction
- **Smart Sectioning**: Splits large images into overlapping sections for better accuracy
- **Text Consolidation**: Intelligently merges overlapping sections to create coherent output
- **Multiple Format Support**: JPG, PNG, BMP, TIFF image formats
- **Batch Processing**: Process multiple images at once
- **Structured Output**: JSON results and individual text files

## Setup

### 1. Install Dependencies

```bash
# Activate your virtual environment (if using one)
# For Windows:
tcsenv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 2. Configure API Key

1. Get your Groq API key from: https://console.groq.com/keys
2. Copy `.env.example` to `.env`
3. Add your API key to the `.env` file:

```
GROQ_API_KEY=your_actual_api_key_here
```

## Usage

### 1. Add Images

Place your handwritten document images in the `input_images/` folder:
- Supported formats: JPG, JPEG, PNG, BMP, TIFF
- For best results, use high-resolution, well-lit images

### 2. Run OCR Processing

```bash
python handwritten_ocr.py
```

### 3. Check Results

Results will be saved in the `output/` folder:
- `ocr_results_TIMESTAMP.json` - Complete processing results
- `extracted_text_TIMESTAMP/` - Individual text files for each image

## Example Output Structure

```
output/
├── ocr_results_20241208_143022.json
└── extracted_text_20241208_143022/
    ├── document1_extracted.txt
    ├── letter2_extracted.txt
    └── notes3_extracted.txt
```

## Tips for Best Results

1. **Image Quality**: Use high-resolution images (300 DPI or higher)
2. **Lighting**: Ensure even lighting without shadows
3. **Contrast**: Dark ink on light paper works best
4. **Orientation**: Keep text right-side up
5. **File Size**: Large images are automatically processed in sections

## Troubleshooting

### Common Issues

1. **API Key Error**: Make sure your Groq API key is correctly set in `.env`
2. **No Images Found**: Check that images are in `input_images/` folder
3. **Poor Recognition**: Try improving image quality or lighting
4. **Memory Issues**: Large images are automatically split into sections

### Error Messages

- `GROQ_API_KEY not found`: Add your API key to `.env` file
- `No image files found`: Place images in `input_images/` folder
- `Error processing image`: Check image format and file integrity

## Advanced Usage

### Custom Processing Parameters

You can modify the OCR tool by editing `handwritten_ocr.py`:

- `sections`: Number of image sections (default: 3)
- `overlap`: Section overlap percentage (default: 0.2)
- `vision_model`: Groq vision model to use
- `text_model`: Groq text model for consolidation

### Supported Models

- Vision: `llama-3.2-90b-vision-preview` (default)
- Text: `llama-3.3-70b-versatile` (default)

## File Structure

```
handwritten-ocr/
├── handwritten_ocr.py      # Main OCR script
├── requirements.txt        # Python dependencies
├── .env                   # API configuration
├── .env.example          # Environment template
├── README.md             # This file
├── input_images/         # Place your images here
└── output/              # Results will be saved here
```

## License

This project is open source and available under the MIT License.
