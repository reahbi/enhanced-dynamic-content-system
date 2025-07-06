#!/usr/bin/env python3
"""
Setup script for Enhanced Dynamic Content System v6.1
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 Setting up Enhanced Dynamic Content System v6.1...")
    
    # Check Python version
    if sys.version_info < (3, 10):
        print("❌ Python 3.10 or higher is required!")
        sys.exit(1)
    
    print("✅ Python version check passed")
    
    # Create virtual environment
    print("\n📦 Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    
    # Determine pip path based on OS
    if os.name == 'nt':  # Windows
        pip_path = Path("venv/Scripts/pip")
        activate_cmd = "venv\\Scripts\\activate"
    else:  # Unix-like
        pip_path = Path("venv/bin/pip")
        activate_cmd = "source venv/bin/activate"
    
    # Upgrade pip
    print("\n📦 Upgrading pip...")
    subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
    
    # Install requirements
    print("\n📦 Installing dependencies...")
    subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
    
    # Create necessary directories
    print("\n📁 Creating directory structure...")
    directories = ["data", "cache", "logs"]
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
    
    # Check for .env file
    env_path = Path("../.env")
    if not env_path.exists():
        print("\n⚠️  Warning: .env file not found in parent directory!")
        print("Please create a .env file with your GEMINI_API_KEY")
        print("Example:")
        print("GEMINI_API_KEY=your-api-key-here")
    else:
        print("\n✅ .env file found")
    
    print("\n✨ Setup complete!")
    print(f"\nTo activate the virtual environment, run:")
    print(f"  {activate_cmd}")
    print("\nTo start the server, run:")
    print("  uvicorn app.main:app --reload")
    print("\nAPI documentation will be available at:")
    print("  http://localhost:8000/docs")

if __name__ == "__main__":
    main()