#!/usr/bin/env python3
"""
Simple runner script for the Human-in-the-Loop Agent.
Ensures environment is set up and runs the Streamlit app.
"""
import os
import sys
import subprocess

def main():
    # Check if .env exists
    if not os.path.exists(".env"):
        print("⚠️  Warning: .env file not found.")
        print("   Copy .env.example to .env and configure your SMTP credentials.")
        print()

    # Check if requirements are installed
    try:
        import streamlit
        import langchain
        import langgraph
    except ImportError:
        print("❌ Dependencies not installed. Run:")
        print("   pip install -r requirements.txt")
        sys.exit(1)

    # Run Streamlit
    print("🚀 Starting Human-in-the-Loop Agent...")
    print("   Open http://localhost:8501 in your browser")
    print()
    subprocess.run(["streamlit", "run", "app.py"])

if __name__ == "__main__":
    main()
