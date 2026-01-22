"""
Script to run the AI Employee Dashboard
"""
import subprocess
import sys
import os
import signal
import time
from pathlib import Path

def install_dependencies():
    """Install required dependencies."""
    print("Installing required dependencies...")

    dependencies = [
        "fastapi",
        "uvicorn",
        "jinja2",
        "python-multipart",
        "markdown",
        "pyyaml"
    ]

    for dep in dependencies:
        try:
            __import__(dep.replace("-", "_"))
            print(f"✓ {dep} already installed")
        except ImportError:
            print(f"Installing {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
            print(f"✓ {dep} installed")

def run_dashboard():
    """Run the FastAPI dashboard."""
    print("Starting AI Employee Dashboard...")
    print("Access the dashboard at: http://localhost:8000")
    print("Press Ctrl+C to stop the server")

    try:
        # Run uvicorn to serve the FastAPI app
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "dashboard_api:app",
            "--host", "127.0.0.1",
            "--port", "8000",
            "--reload"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running dashboard: {e}")
    except KeyboardInterrupt:
        print("\nDashboard stopped by user")

if __name__ == "__main__":
    print("AI Employee Dashboard Setup")
    print("="*40)

    # Install dependencies
    install_dependencies()

    print("\nDependencies installed successfully!")
    print("\nStarting dashboard...")

    # Run the dashboard
    run_dashboard()