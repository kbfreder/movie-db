#!/usr/bin/env python3
"""
Test script to verify the setup of the Movie Database Query Web App
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_dependencies():
    """Check if required Python packages are installed"""
    required_packages = [
        'fastapi',
        'uvicorn', 
        'openai',
        'dotenv',
        'pydantic'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - MISSING")
    
    if missing_packages:
        print(f"\n📦 Install missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found")
        print("📝 Create .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
        return False
    
    # Check if OPENAI_API_KEY is set
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        print("❌ OPENAI_API_KEY not set in .env file")
        return False
    
    print("✅ .env file configured")
    return True

def check_node_dependencies():
    """Check if Node.js dependencies are installed"""
    frontend_dir = Path('frontend')
    if not frontend_dir.exists():
        print("❌ frontend directory not found")
        return False
    
    node_modules = frontend_dir / 'node_modules'
    if not node_modules.exists():
        print("❌ Node.js dependencies not installed")
        print("📦 Run: cd frontend && npm install")
        return False
    
    print("✅ Node.js dependencies installed")
    return True

def test_backend():
    """Test if backend can start"""
    try:
        # Test import
        sys.path.append('backend')
        from main import app
        print("✅ Backend imports successfully")
        return True
    except Exception as e:
        print(f"❌ Backend import failed: {e}")
        return False

def main():
    print("🔍 Testing Movie Database Query Web App Setup\n")
    
    tests = [
        ("Python Dependencies", check_python_dependencies),
        ("Environment Configuration", check_env_file),
        ("Node.js Dependencies", check_node_dependencies),
        ("Backend Import", test_backend)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        if test_func():
            passed += 1
        print()
    
    print(f"🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! You can now run the application:")
        print("   ./start.sh")
        print("\nOr start services individually:")
        print("   Backend:  cd backend && python main.py")
        print("   Frontend: cd frontend && npm start")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 