#!/usr/bin/env python3
"""
Startup script for Trading Signals Backend
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Start the backend server"""
    print("🚀 Starting Trading Signals Backend...")
    
    # Check if virtual environment exists
    venv_path = Path("venv")
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    
    # Determine activation script
    if os.name == 'nt':  # Windows
        activate_script = "venv\\Scripts\\activate"
        python_path = "venv\\Scripts\\python.exe"
    else:  # Unix/Linux/Mac
        activate_script = "venv/bin/activate"
        python_path = "venv/bin/python"
    
    # Install requirements if needed
    print("📥 Installing dependencies...")
    try:
        subprocess.run([python_path, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Error installing dependencies. Please check requirements.txt")
        return
    
    # Start the server
    print("🔥 Starting FastAPI server...")
    try:
        subprocess.run([python_path, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
        return

if __name__ == "__main__":
    main()

