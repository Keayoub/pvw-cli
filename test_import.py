#!/usr/bin/env python3
"""
Test FastAPI app import
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

print(f"Current working directory: {os.getcwd()}")
print(f"Backend path: {backend_path}")
print(f"Backend exists: {os.path.exists(backend_path)}")
print(f"Python path includes: {sys.path[:3]}")

try:
    print("Attempting to import main...")
    from main import app
    print("SUCCESS: FastAPI app imported successfully")
    print(f"App type: {type(app)}")
    print(f"App title: {app.title}")
except Exception as e:
    print(f"ERROR: Failed to import app: {e}")
    import traceback
    traceback.print_exc()
