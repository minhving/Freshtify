#!/usr/bin/env python3
"""
Dependency installation script for AI Stock Level Estimation API.
This script handles installation with proper error handling and fallbacks.
"""

import sys
import subprocess
import os
import importlib.util

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✓ Python version: {sys.version.split()[0]}")
    return True

def install_package(package_name, import_name=None):
    """Install a single package with error handling."""
    if import_name is None:
        import_name = package_name.replace('-', '_')
    
    try:
        # Check if already installed
        spec = importlib.util.find_spec(import_name)
        if spec is not None:
            print(f"✓ {package_name} already installed")
            return True
    except ImportError:
        pass
    
    print(f"Installing {package_name}...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", package_name
        ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"✓ {package_name} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}: {e}")
        return False

def install_from_requirements(requirements_file):
    """Install packages from requirements file."""
    if not os.path.exists(requirements_file):
        print(f"❌ Requirements file {requirements_file} not found")
        return False
    
    print(f"Installing packages from {requirements_file}...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", requirements_file
        ])
        print(f"✓ Packages from {requirements_file} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install from {requirements_file}: {e}")
        return False

def install_core_dependencies():
    """Install core dependencies first."""
    core_packages = [
        "fastapi",
        "uvicorn[standard]",
        "python-multipart",
        "pydantic",
        "python-dotenv",
        "httpx",
        "aiofiles",
        "loguru",
        "psutil"
    ]
    
    print("Installing core dependencies...")
    failed_packages = []
    
    for package in core_packages:
        if not install_package(package):
            failed_packages.append(package)
    
    if failed_packages:
        print(f"❌ Failed to install: {', '.join(failed_packages)}")
        return False
    
    print("✓ Core dependencies installed successfully")
    return True

def install_ai_dependencies():
    """Install AI/ML dependencies."""
    ai_packages = [
        "torch",
        "torchvision", 
        "transformers",
        "opencv-python",
        "Pillow",
        "numpy"
    ]
    
    print("Installing AI/ML dependencies...")
    failed_packages = []
    
    for package in ai_packages:
        if not install_package(package):
            failed_packages.append(package)
    
    if failed_packages:
        print(f"⚠️  Some AI packages failed to install: {', '.join(failed_packages)}")
        print("The API will still work with basic functionality")
        return False
    
    print("✓ AI/ML dependencies installed successfully")
    return True

def test_installation():
    """Test if the installation works."""
    print("Testing installation...")
    
    try:
        # Test core imports
        import fastapi
        import uvicorn
        import pydantic
        print("✓ Core API components working")
        
        # Test AI imports
        try:
            import torch
            import cv2
            import numpy as np
            print("✓ AI/ML components working")
            print(f"✓ PyTorch version: {torch.__version__}")
            print(f"✓ CUDA available: {torch.cuda.is_available()}")
        except ImportError as e:
            print(f"⚠️  AI/ML components not fully working: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Installation test failed: {e}")
        return False

def main():
    """Main installation function."""
    print("AI Stock Level Estimation API - Dependency Installer")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install core dependencies
    if not install_core_dependencies():
        print("❌ Core dependency installation failed")
        return 1
    
    # Install AI dependencies
    install_ai_dependencies()
    
    # Test installation
    if not test_installation():
        print("❌ Installation test failed")
        return 1
    
    print("\n" + "=" * 60)
    print("🎉 Installation completed successfully!")
    print("\nNext steps:")
    print("1. Run: python start_server.py")
    print("2. Visit: http://localhost:8000/docs")
    print("3. Test the API with your images")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
