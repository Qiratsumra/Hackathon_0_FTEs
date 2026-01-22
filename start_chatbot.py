#!/usr/bin/env python3
"""
Startup script for the AI Employee Chatbot

This script initializes and runs the AI Employee Chatbot interface.
"""

import sys
import os
from pathlib import Path

def main():
    """Main entry point for the chatbot."""
    print("🚀 Starting AI Employee Chatbot...")

    # Add the current directory to the path so we can import our modules
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))

    try:
        # Import and run the chatbot
        from ai_employee_chatbot import main as chatbot_main
        print("✅ AI Employee Chatbot loaded successfully!")
        print("💬 You can now interact with the AI Employee System")
        print("-" * 50)

        chatbot_main()

    except ImportError as e:
        print(f"❌ Failed to import chatbot: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running chatbot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()