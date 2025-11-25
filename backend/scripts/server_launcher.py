#!/usr/bin/env python3
"""
AlphaForge Backend Server Launcher
Keeps the server running continuously
"""

import subprocess
import sys
import os
import time

def main():
    print("\n" + "="*60)
    print("🚀 Starting AlphaForge Backend Server")
    print("="*60)
    print("📡 Server: http://localhost:5000")
    print("📖 Docs: http://localhost:5000/docs")
    print("🔍 Health: http://localhost:5000/health")
    print("="*60)

    # Change to the backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)

    while True:
        try:
            # Start the server
            cmd = [
                sys.executable, "-m", "uvicorn",
                "app:app",
                "--host", "127.0.0.1",
                "--port", "5000",
                "--log-level", "info",
                "--reload"
            ]

            print(f"\n🔄 Starting server process...")
            process = subprocess.run(cmd)

            if process.returncode == 0:
                print("✅ Server exited normally")
                break
            else:
                print(f"⚠️  Server exited with code {process.returncode}, restarting in 3 seconds...")
                time.sleep(3)

        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
            break
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            print("🔄 Retrying in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    main()