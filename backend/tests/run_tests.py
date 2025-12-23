#!/usr/bin/env python3
"""
Test runner script for the Glam Cart Builder API.
This script starts the server and runs all tests.
"""

import subprocess
import sys
import time
import os
import signal
import requests
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

def wait_for_server(url="http://localhost:8000/health", timeout=30):
    """Wait for the server to be ready."""
    print(f"⏳ Waiting for server at {url}...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(1)
    
    print("❌ Server failed to start within timeout")
    return False

def run_tests():
    """Run the test suite."""
    print("🧪 Running test suite...")
    
    # Run pytest with verbose output
    cmd = [
        sys.executable, "-m", "pytest",
        "-v",
        "--tb=short",
        "--color=yes",
        "tests/",
    ]
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode == 0

def main():
    """Main test runner function."""
    print("🚀 Glam Cart Builder API Test Runner")
    print("=" * 50)
    
    # Check if server is already running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("📍 Server is already running")
            server_process = None
        else:
            raise requests.exceptions.RequestException()
    except requests.exceptions.RequestException:
        # Start the server
        print("🔧 Starting test server...")
        server_process = subprocess.Popen([
            sys.executable, "run.py"
        ], cwd=Path(__file__).parent.parent)
        
        # Wait for server to be ready
        if not wait_for_server():
            if server_process:
                server_process.terminate()
            sys.exit(1)
    
    try:
        # Run tests
        success = run_tests()
        
        if success:
            print("\n✅ All tests passed!")
            exit_code = 0
        else:
            print("\n❌ Some tests failed!")
            exit_code = 1
            
    finally:
        # Clean up server if we started it
        if server_process:
            print("🛑 Stopping test server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server_process.kill()
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
