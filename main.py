#!/usr/bin/env python3
"""
Main entry point for Render deployment
This file is at the root level and can properly import from my_taskflow
"""

# Import the FastAPI app from the proper location
from my_taskflow.backend.api import app

# This makes the app available at the module level
__all__ = ['app']

if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
