#!/usr/bin/env python3
"""
Test script to validate the handwritten OCR setup
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def test_environment():
    """Test environment setup"""
    print("🧪 Testing Environment Setup")
    print("-" * 40)
    
    # Test .env file
    if not Path(".env").exists():
        print("❌ .env file not found")
        return False
    
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("❌ GROQ_API_KEY not set in .env file")
        print("   Please add your Groq API key to the .env file")
        return False
    
    if api_key == "your_groq_api_key_here" or len(api_key) < 10:
        print("❌ GROQ_API_KEY appears to be placeholder or invalid")
        print("   Please set a valid Groq API key in the .env file")
        return False
    
    print("✅ Environment variables configured")
    return True

def test_dependencies():
    """Test required dependencies"""
    print("\n🧪 Testing Dependencies")
    print("-" * 40)
    
    required_packages = [
        "PIL",
        "langchain_groq", 
        "dotenv",
        "pathlib",
        "json",
        "base64",
        "io"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == "PIL":
                import PIL
            elif package == "langchain_groq":
                import langchain_groq
            elif package == "dotenv":
                import dotenv
            elif package == "pathlib":
                import pathlib
            elif package == "json":
                import json
            elif package == "base64":
                import base64
            elif package == "io":
                import io
            
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    return True

def test_directories():
    """Test directory structure"""
    print("\n🧪 Testing Directory Structure")
    print("-" * 40)
    
    required_dirs = ["input_images", "output"]
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"❌ {dir_name}/ directory missing")
            try:
                dir_path.mkdir(exist_ok=True)
                print(f"   ✅ Created {dir_name}/ directory")
            except Exception as e:
                print(f"   ❌ Failed to create {dir_name}/: {e}")
                return False
    
    return True

def test_api_connection():
    """Test API connection (optional - requires valid API key)"""
    print("\n🧪 Testing API Connection")
    print("-" * 40)
    
    try:
        from langchain_groq import ChatGroq
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_groq_api_key_here":
            print("⚠️  Skipping API test - no valid API key")
            return True
        
        # Simple test with minimal request
        groq_llm = ChatGroq(
            groq_api_key=api_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0
        )
        
        # Test with a simple message
        response = groq_llm.invoke([{"role": "user", "content": "Hello"}])
        
        if response and response.content:
            print("✅ API connection successful")
            return True
        else:
            print("❌ API connection failed - no response")
            return False
            
    except Exception as e:
        print(f"❌ API connection failed: {str(e)}")
        return False

def check_sample_images():
    """Check for sample images in input directory"""
    print("\n🧪 Checking for Sample Images")
    print("-" * 40)
    
    input_dir = Path("input_images")
    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    
    image_files = [
        f for f in input_dir.iterdir() 
        if f.is_file() and f.suffix.lower() in supported_formats
    ]
    
    if image_files:
        print(f"✅ Found {len(image_files)} image file(s):")
        for img_file in image_files:
            print(f"   • {img_file.name}")
        return True
    else:
        print("⚠️  No image files found in input_images/")
        print("   Add some handwritten document images to test the OCR")
        return True  # Not a failure, just a warning

def main():
    """Run all tests"""
    print("🚀 Handwritten OCR Setup Validation")
    print("=" * 50)
    
    tests = [
        ("Environment", test_environment),
        ("Dependencies", test_dependencies),
        ("Directories", test_directories),
        ("Sample Images", check_sample_images),
        ("API Connection", test_api_connection),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test failed with error: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Add handwritten document images to input_images/")
        print("2. Run: python handwritten_ocr.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
