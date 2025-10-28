#!/usr/bin/env python3
"""
Startup script for the AI Stock Level Estimation API.
This script will check dependencies and start the server.
"""

import sys
import subprocess
import os

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'torch',
        'transformers',
        'opencv-python',
        'Pillow',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies():
    """Install missing dependencies."""
    print("Installing missing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False

def start_server():
    """Start the FastAPI server."""
    try:
        print("Starting AI Stock Level Estimation API server...")
        print("Server will be available at: http://localhost:8000")
        print("API Documentation: http://localhost:8000/docs")
        print("Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Import and run the server
        from app.main import app
        import uvicorn
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"✗ Failed to start server: {e}")
        return False

def main():
    """Main function."""
    print("AI Stock Level Estimation API - Startup Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("app") or not os.path.exists("requirements.txt"):
        print("Please run this script from the project root directory")
        print("Make sure 'app' folder and 'requirements.txt' exist")
        return 1
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print("Installing dependencies...")
        
        if not install_dependencies():
            print("Failed to install dependencies")
            print("Please install manually: pip install -r requirements.txt")
            return 1
    print("All dependencies are available")
    
    # Start server
    start_server()
    return 0

if __name__ == "__main__":
    sys.exit(main())
