#!/usr/bin/env python3
"""
Simple backend server startup script for testing
"""
import sys
import subprocess
from pathlib import Path

def start_server():
    """Start the backend server"""
    backend_dir = Path(__file__).parent / "backend"
    
    try:
        print("🚀 Starting Purview CLI v2.0 Backend Server...")
        print(f"📁 Backend directory: {backend_dir}")
        
        # Change to backend directory and start server
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ]
        
        subprocess.run(cmd, cwd=backend_dir, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Server error: {e}")
        return False

if __name__ == "__main__":
    start_server()
