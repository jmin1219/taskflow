#!/usr/bin/env python3
"""
Startup script for production deployment
Initializes database before starting the server
"""

import subprocess
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Initialize database
from my_taskflow.backend.database import init_db

print("🚀 Initializing TaskFlow database...")
init_db()
print("✅ Database ready!")

# Start the server
print("🌐 Starting TaskFlow API server...")
subprocess.run([
    "uvicorn", 
    "my_taskflow.backend.api:app",
    "--host", "0.0.0.0",
    "--port", str(os.environ.get("PORT", 8000))
])
