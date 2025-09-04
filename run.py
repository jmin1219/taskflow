#!/usr/bin/env python3
"""
Startup script for Render deployment
Handles module imports correctly
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Start the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("my_taskflow.backend.api:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
