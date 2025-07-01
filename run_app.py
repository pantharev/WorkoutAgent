#!/usr/bin/env python3
"""
Launch script for Workout Agent
Starts both the API server and Streamlit UI
"""

import subprocess
import time
import sys
import os
import signal
import threading
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import fastapi
        import uvicorn
        import pydantic_ai
        import requests
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has OpenAI API key"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("Please copy .env.example to .env and add your OpenAI API key")
        return False
    
    try:
        with open(".env", "r") as f:
            content = f.read()
            if "OPENAI_API_KEY=" in content and "your_openai_api_key_here" not in content:
                print("✅ OpenAI API key found in .env file")
                return True
            else:
                print("⚠️  OpenAI API key not set in .env file")
                print("Please add your OpenAI API key to the .env file")
                return False
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False

def start_api_server():
    """Start the FastAPI server"""
    print("🚀 Starting API server...")
    try:
        # Start the API server
        process = subprocess.Popen([
            sys.executable, "workout_agent.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ API server started successfully")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ API server failed to start:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return None
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        return None

def start_streamlit():
    """Start the Streamlit app"""
    print("🎨 Starting Streamlit UI...")
    try:
        # Start Streamlit
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        time.sleep(2)
        
        if process.poll() is None:
            print("✅ Streamlit UI started successfully")
            print("🌐 Open your browser to: http://localhost:8501")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Streamlit failed to start:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return None
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        return None

def main():
    """Main function to launch both services"""
    try:
        print("🏋️  Workout Agent Launcher")
    except UnicodeEncodeError:
        print("Workout Agent Launcher")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    env_ready = check_env_file()
    if not env_ready:
        print("\n⚠️  You can still run the app, but AI features won't work without the API key")
        response = input("Continue anyway? (y/n): ").lower().strip()
        if response != 'y':
            sys.exit(1)
    
    print("\n🚀 Starting services...")
    
    # Start API server
    api_process = start_api_server()
    if not api_process:
        print("❌ Failed to start API server")
        sys.exit(1)
    
    # Start Streamlit
    streamlit_process = start_streamlit()
    if not streamlit_process:
        print("❌ Failed to start Streamlit")
        if api_process:
            api_process.terminate()
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Workout Agent is now running!")
    print("📊 API Server: http://localhost:8000")
    print("🎨 Streamlit UI: http://localhost:8501")
    print("📖 API Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop both services")
    print("=" * 50)
    
    try:
        # Keep the script running and monitor processes
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if api_process.poll() is not None:
                print("❌ API server stopped unexpectedly")
                break
            
            if streamlit_process.poll() is not None:
                print("❌ Streamlit stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        
        # Terminate processes
        if api_process and api_process.poll() is None:
            api_process.terminate()
            print("✅ API server stopped")
        
        if streamlit_process and streamlit_process.poll() is None:
            streamlit_process.terminate()
            print("✅ Streamlit UI stopped")
        
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
