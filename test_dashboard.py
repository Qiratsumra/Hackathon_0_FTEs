"""
Test script to verify the dashboard is working
"""
import requests
import time
import subprocess
import sys
from threading import Thread

def start_server():
    """Start the server in a separate process."""
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "dashboard_api:app",
        "--host", "127.0.0.1",
        "--port", "8000"
    ])

def test_dashboard():
    """Test if the dashboard is accessible."""
    # Wait a bit for the server to start
    time.sleep(3)

    try:
        response = requests.get("http://127.0.0.1:8000")
        if response.status_code == 200:
            print("✅ Dashboard is accessible!")
            print("🌐 Visit http://localhost:8000 to access your AI Employee Dashboard")
            return True
        else:
            print(f"❌ Dashboard returned status code: {response.status_code}")
            return False
    except requests.ConnectionError:
        print("❌ Could not connect to dashboard. Make sure it's running on port 8000.")
        return False
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")
        return False

if __name__ == "__main__":
    print("Testing AI Employee Dashboard...")

    # Start server in background
    server_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn",
        "dashboard_api:app",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--reload"
    ])

    try:
        # Test the dashboard
        success = test_dashboard()

        if success:
            print("\n🎉 AI Employee Dashboard is ready!")
            print("📋 You can now:")
            print("   - View tasks in different statuses")
            print("   - Approve/reject pending tasks")
            print("   - Move tasks between statuses")
            print("   - View detailed task information")
            print("\n💡 Tip: Keep this server running to access the dashboard")
        else:
            print("\n❌ Dashboard test failed.")

        print("\nPress Ctrl+C to stop the server")

        # Wait for user to stop the server
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping server...")

    finally:
        server_process.terminate()
        server_process.wait()