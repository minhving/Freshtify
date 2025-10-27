#!/usr/bin/env python3
"""
Simple startup script that bypasses .env configuration issues.
"""

import sys
import os
import uvicorn

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def start_server():
    """Start the FastAPI server with hardcoded settings."""
    try:
        print("Starting AI Stock Level Estimation API server...")
        print("Server will be available at: http://localhost:8000")
        print("API Documentation: http://localhost:8000/docs")
        print("Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Start server with hardcoded configuration
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n✓ Server stopped by user")
    except Exception as e:
        print(f"✗ Failed to start server: {e}")
        return False

if __name__ == "__main__":
    start_server()
