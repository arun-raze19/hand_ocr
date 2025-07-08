#!/usr/bin/env python3
"""
Debug script to check environment variable loading
"""

import os
from dotenv import load_dotenv
from pathlib import Path

print("🔍 Environment Debug Information")
print("=" * 50)

# Check if .env file exists
env_file = Path(".env")
print(f"📄 .env file exists: {env_file.exists()}")

if env_file.exists():
    print(f"📄 .env file size: {env_file.stat().st_size} bytes")
    
    # Read and display .env content (safely)
    with open(env_file, 'r') as f:
        content = f.read()
        lines = content.split('\n')
        print(f"📄 .env file lines: {len(lines)}")
        
        for i, line in enumerate(lines, 1):
            if line.strip() and not line.strip().startswith('#'):
                if 'GROQ_API_KEY' in line:
                    key_part = line.split('=')[0]
                    value_part = line.split('=', 1)[1] if '=' in line else ''
                    print(f"   Line {i}: {key_part}=<{len(value_part)} chars>")
                else:
                    print(f"   Line {i}: {line}")

print("\n🔧 Before load_dotenv():")
print(f"   GROQ_API_KEY in os.environ: {'GROQ_API_KEY' in os.environ}")
print(f"   GROQ_API_KEY value: {repr(os.environ.get('GROQ_API_KEY'))}")

# Load environment variables
print("\n⚡ Loading .env file...")
load_result = load_dotenv()
print(f"   load_dotenv() returned: {load_result}")

print("\n🔧 After load_dotenv():")
print(f"   GROQ_API_KEY in os.environ: {'GROQ_API_KEY' in os.environ}")
api_key = os.getenv('GROQ_API_KEY')
print(f"   GROQ_API_KEY value: {repr(api_key)}")
print(f"   GROQ_API_KEY length: {len(api_key) if api_key else 0}")
print(f"   GROQ_API_KEY is None: {api_key is None}")
print(f"   GROQ_API_KEY is empty: {api_key == '' if api_key is not None else 'N/A'}")

# Test the exact same logic as in handwritten_ocr.py
print("\n🧪 Testing HandwrittenOCR logic:")
try:
    groq_api_key = os.getenv("GROQ_API_KEY")
    print(f"   Retrieved key: {repr(groq_api_key)}")
    
    if not groq_api_key:
        print("   ❌ Key evaluation failed - would raise ValueError")
        print(f"   Truthiness test: bool(groq_api_key) = {bool(groq_api_key)}")
    else:
        print("   ✅ Key evaluation passed")
        
except Exception as e:
    print(f"   ❌ Exception: {e}")

print("\n" + "=" * 50)
