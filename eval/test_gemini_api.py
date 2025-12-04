#!/usr/bin/env python3
"""
Test Gemini API call to diagnose issues.
"""
import sys
from pathlib import Path
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import google.generativeai as genai
    print("✅ google-generativeai imported successfully")
except ImportError as e:
    print(f"❌ Failed to import google-generativeai: {e}")
    sys.exit(1)

# Load API key
env_path = Path(__file__).parent.parent / "env" / ".env"
api_key = None

if env_path.exists():
    print(f"📁 Reading .env file: {env_path}")
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                break

if not api_key:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key or api_key == "your_key_here":
    print("❌ GEMINI_API_KEY not found in .env file or environment variables")
    sys.exit(1)

print(f"✅ API key found (length: {len(api_key)})")
print(f"   First 10 chars: {api_key[:10]}...")

# Configure client
try:
    genai.configure(api_key=api_key)
    print("✅ genai.configure() successful")
except Exception as e:
    print(f"❌ Failed to configure genai: {e}")
    sys.exit(1)

# Load model
try:
    model = genai.GenerativeModel("gemini-2.0-flash")
    print("✅ Model loaded: gemini-2.0-flash")
except Exception as e:
    print(f"❌ Failed to load model: {e}")
    sys.exit(1)

# Test API call
print("\n🧪 Testing API call...")
try:
    response = model.generate_content("Say 'Hello, this is a test' in exactly 5 words.")
    print(f"✅ API call successful!")
    print(f"   Response: {response.text}")
except Exception as e:
    print(f"❌ API call failed: {e}")
    print(f"   Error type: {type(e).__name__}")
    if hasattr(e, 'message'):
        print(f"   Error message: {e.message}")
    if hasattr(e, 'args'):
        print(f"   Error args: {e.args}")
    sys.exit(1)

print("\n✅ All tests passed!")

