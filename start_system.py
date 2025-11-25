"""
AlphaForge Complete System Startup Script
Starts backend server + automated scheduler
"""

import subprocess
import sys
import time
import os
import signal

def start_system():
    """Start both backend and scheduler"""
    print("\n" + "="*80)
    print("🚀 AlphaForge Trading System - Complete Startup")
    print("="*80 + "\n")
    
    # Change to backend directory
    os.chdir('backend')
    
    processes = []
    
    try:
        # Start backend server
        print("📡 Starting backend API server...")
        backend_process = subprocess.Popen(
            [sys.executable, "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        processes.append(('Backend', backend_process))
        print("✅ Backend server starting on port 5000...\n")
        
        # Wait for backend to be ready
        print("⏳ Waiting for backend to initialize (5 seconds)...")
        time.sleep(5)
        
        # Start scheduler
        print("\n⏰ Starting automated signal scheduler...")
        scheduler_process = subprocess.Popen(
            [sys.executable, "signal_scheduler.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        processes.append(('Scheduler', scheduler_process))
        print("✅ Scheduler starting (runs every 5 minutes)...\n")
        
        print("="*80)
        print("✅ SYSTEM RUNNING")
        print("="*80)
        print("\n📊 Active Components:")
        print("   1. Backend API Server (http://localhost:5000)")
        print("   2. Automated Signal Scheduler (every 5 minutes)")
        print("   3. Gemini AI Validation (if API key configured)")
        print("\n🌐 Access:")
        print("   - API Documentation: http://localhost:5000/docs")
        print("   - Health Check: http://localhost:5000/health")
        print("   - Frontend: http://localhost:3000 (start separately)")
        print("\n📝 Logs:")
        print("   - Backend: Check terminal output")
        print("   - Scheduler: signal_scheduler.log")
        print("\n🛑 Press Ctrl+C to stop all services\n")
        print("="*80 + "\n")
        
        # Stream output from both processes
        while True:
            for name, process in processes:
                if process.poll() is not None:
                    print(f"\n❌ {name} process ended unexpectedly!")
                    return
                
                # Read output
                try:
                    line = process.stdout.readline()
                    if line:
                        print(f"[{name}] {line}", end='')
                except:
                    pass
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\n" + "="*80)
        print("🛑 Shutting down system...")
        print("="*80 + "\n")
        
        # Terminate all processes
        for name, process in processes:
            print(f"   Stopping {name}...")
            process.terminate()
            try:
                process.wait(timeout=5)
                print(f"   ✅ {name} stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"   ⚠️  {name} force killed")
        
        print("\n✅ System shutdown complete")
        print("="*80 + "\n")
        sys.exit(0)

if __name__ == "__main__":
    # Check if we're in the right directory
    if not os.path.exists('backend'):
        print("❌ Error: Please run this script from the AlphaForge root directory")
        print("Example: python start_system.py")
        sys.exit(1)
    
    start_system()
