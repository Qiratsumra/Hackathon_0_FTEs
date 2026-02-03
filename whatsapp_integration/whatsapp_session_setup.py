"""
WhatsApp Session Setup Script
------------------------------
This script helps you authenticate with WhatsApp Web and save the session
for automated monitoring by the WhatsApp watcher.

Run this script ONCE to setup your WhatsApp session.

Usage:
    python whatsapp_session_setup.py

Author: AI Employee Project
Version: 1.0
"""

import os
import sys
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("❌ Error: Playwright not installed!")
    print("\n💡 Please install it first:")
    print("   pip install playwright playwright-stealth")
    print("   python -m playwright install chromium")
    sys.exit(1)


class WhatsAppSessionSetup:
    """Handles WhatsApp Web session setup and validation"""
    
    def __init__(self, session_path: str = "./whatsapp_session"):
        """
        Initialize the session setup
        
        Args:
            session_path: Directory where session data will be stored
        """
        self.session_path = Path(session_path)
        self.session_path.mkdir(exist_ok=True, parents=True)
        print(f"📁 Session directory: {self.session_path.absolute()}")
        
    def setup_session(self):
        """
        Opens WhatsApp Web and waits for user to scan QR code.
        Session is saved for future use.
        
        Returns:
            bool: True if setup successful, False otherwise
        """
        print("\n" + "="*70)
        print("🚀 WHATSAPP SESSION SETUP")
        print("="*70)
        print("\n📱 You will need your phone to scan the QR code")
        print("💡 Make sure WhatsApp is installed on your phone")
        print("💡 Make sure your phone has internet connection")
        print("\nPress Enter to continue...")
        input()
        
        try:
            with sync_playwright() as p:
                print("\n🌐 Opening browser...")
                
                # Launch browser with persistent context (saves session)
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=False,  # Must be False to show QR code
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                    ]
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                print("🌍 Loading WhatsApp Web...")
                page.goto('https://web.whatsapp.com', wait_until='domcontentloaded')
                
                print("\n" + "="*70)
                print("📱 SCAN THE QR CODE WITH YOUR PHONE NOW!")
                print("="*70)
                print("\nHow to scan:")
                print("1. Open WhatsApp on your phone")
                print("2. Tap Menu (⋮) or Settings")
                print("3. Tap 'Linked Devices'")
                print("4. Tap 'Link a Device'")
                print("5. Point your phone at the QR code on screen")
                print("\n⏳ Waiting for you to scan... (timeout: 2 minutes)")
                print("="*70 + "\n")
                
                try:
                    # Wait for chat list to appear (means successfully logged in)
                    page.wait_for_selector(
                        '[data-testid="chat-list"]',
                        timeout=120000  # 2 minutes
                    )
                    
                    print("\n" + "="*70)
                    print("✅ SUCCESS! You are now logged in!")
                    print("="*70)
                    print(f"\n💾 Session saved to: {self.session_path.absolute()}")
                    print("\n✨ What this means:")
                    print("   - You won't need to scan QR code again")
                    print("   - The watcher can now monitor your WhatsApp automatically")
                    print("   - Your session is stored locally and securely")
                    print("\n💡 Next steps:")
                    print("   1. You can close this browser window now")
                    print("   2. Run the watcher: python whatsapp_watcher_complete.py")
                    print("   3. Or integrate with orchestrator")
                    print("\n🔒 Security reminder:")
                    print("   - Never share the whatsapp_session/ folder")
                    print("   - Add it to .gitignore (don't commit to git)")
                    
                    # Keep browser open for a few seconds
                    print("\n⏳ Closing browser in 10 seconds...")
                    time.sleep(10)
                    
                    browser.close()
                    return True
                    
                except PlaywrightTimeout:
                    print("\n" + "="*70)
                    print("❌ LOGIN TIMEOUT")
                    print("="*70)
                    print("\n⏱️  You didn't scan the QR code in time (2 minutes)")
                    print("\n💡 Please try again:")
                    print("   1. Make sure your phone is ready")
                    print("   2. Have WhatsApp open")
                    print("   3. Run this script again")
                    browser.close()
                    return False
                    
        except Exception as e:
            print(f"\n❌ Error during setup: {e}")
            print("\n💡 Troubleshooting:")
            print("   1. Make sure Chromium is installed: python -m playwright install chromium")
            print("   2. Check your internet connection")
            print("   3. Try running the script again")
            return False
    
    def test_session(self):
        """
        Test if the saved session is still valid
        
        Returns:
            bool: True if session is valid, False otherwise
        """
        print("\n" + "="*70)
        print("🔍 TESTING SAVED SESSION")
        print("="*70)
        
        if not self.session_path.exists():
            print("\n❌ No session found!")
            print(f"   Expected location: {self.session_path.absolute()}")
            print("\n💡 You need to run setup first (Option 1)")
            return False
        
        print(f"\n📁 Found session at: {self.session_path.absolute()}")
        print("🌐 Opening WhatsApp Web in headless mode...")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=True  # Don't show browser for test
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto('https://web.whatsapp.com', wait_until='domcontentloaded')
                
                try:
                    # Wait for chat list (means logged in)
                    page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
                    
                    # Get some basic info
                    chats = page.query_selector_all('[data-testid="cell-frame-container"]')
                    
                    print("\n" + "="*70)
                    print("✅ SESSION IS VALID AND WORKING!")
                    print("="*70)
                    print(f"\n📊 Session info:")
                    print(f"   - Status: Active")
                    print(f"   - Chats visible: {len(chats)}")
                    print(f"   - Location: {self.session_path.absolute()}")
                    print("\n✨ Your WhatsApp watcher is ready to use!")
                    print("\n💡 Next steps:")
                    print("   - Run: python whatsapp_watcher_complete.py")
                    print("   - Or add to your orchestrator")
                    
                    browser.close()
                    return True
                    
                except PlaywrightTimeout:
                    print("\n" + "="*70)
                    print("❌ SESSION EXPIRED OR INVALID")
                    print("="*70)
                    print("\n⚠️  The saved session is no longer valid")
                    print("\n💡 You need to login again:")
                    print("   1. Run this script again")
                    print("   2. Choose Option 1 (Setup new session)")
                    print("   3. Scan QR code with your phone")
                    
                    browser.close()
                    return False
                    
        except Exception as e:
            print(f"\n❌ Error testing session: {e}")
            print("\n💡 Try setting up a new session (Option 1)")
            return False
    
    def clear_session(self):
        """
        Delete the saved session (useful for troubleshooting)
        
        Returns:
            bool: True if cleared successfully
        """
        print("\n" + "="*70)
        print("🗑️  CLEAR SESSION")
        print("="*70)
        
        if not self.session_path.exists():
            print("\n✅ No session to clear")
            return True
        
        print(f"\n⚠️  This will delete: {self.session_path.absolute()}")
        print("   You will need to scan QR code again to login")
        
        confirm = input("\n❓ Are you sure? (yes/no): ").strip().lower()
        
        if confirm in ['yes', 'y']:
            try:
                import shutil
                shutil.rmtree(self.session_path)
                print("\n✅ Session cleared successfully!")
                print("💡 Run Option 1 to setup a new session")
                return True
            except Exception as e:
                print(f"\n❌ Error clearing session: {e}")
                return False
        else:
            print("\n↩️  Cancelled")
            return False


def show_menu():
    """Display the main menu"""
    print("\n" + "="*70)
    print("          WHATSAPP SESSION SETUP TOOL")
    print("="*70)
    print("\n📱 Choose an option:\n")
    print("  1. Setup new session (scan QR code)")
    print("  2. Test existing session")
    print("  3. Clear session (logout)")
    print("  4. Show session info")
    print("  5. Exit")
    print("\n" + "="*70)


def show_session_info(session_path: Path):
    """Display information about the session"""
    print("\n" + "="*70)
    print("📊 SESSION INFORMATION")
    print("="*70)
    
    print(f"\n📁 Session location: {session_path.absolute()}")
    
    if session_path.exists():
        print("   Status: ✅ Exists")
        
        # Get folder size
        total_size = sum(f.stat().st_size for f in session_path.rglob('*') if f.is_file())
        size_mb = total_size / (1024 * 1024)
        print(f"   Size: {size_mb:.2f} MB")
        
        # Get file count
        file_count = len(list(session_path.rglob('*')))
        print(f"   Files: {file_count}")
        
        print("\n💡 To use this session:")
        print("   - Run: python whatsapp_watcher_complete.py")
        print("   - Or add WhatsAppWatcher to your orchestrator")
        
    else:
        print("   Status: ❌ Not found")
        print("\n💡 You need to setup a session first (Option 1)")


def main():
    """Main entry point"""
    
    # Check if playwright is installed
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("\n" + "="*70)
        print("❌ PLAYWRIGHT NOT INSTALLED")
        print("="*70)
        print("\n💡 Install it first:")
        print("\n   pip install playwright playwright-stealth")
        print("   python -m playwright install chromium")
        print("\n" + "="*70)
        sys.exit(1)
    
    # Get session path from environment or use default
    session_path = os.getenv('WHATSAPP_SESSION_PATH', './whatsapp_session')
    setup = WhatsAppSessionSetup(session_path=session_path)
    
    while True:
        show_menu()
        choice = input("\n👉 Enter your choice (1-5): ").strip()
        
        if choice == "1":
            # Setup new session
            success = setup.setup_session()
            if success:
                print("\n✅ Setup complete!")
            else:
                print("\n❌ Setup failed. Please try again.")
            input("\nPress Enter to continue...")
            
        elif choice == "2":
            # Test existing session
            setup.test_session()
            input("\nPress Enter to continue...")
            
        elif choice == "3":
            # Clear session
            setup.clear_session()
            input("\nPress Enter to continue...")
            
        elif choice == "4":
            # Show session info
            show_session_info(setup.session_path)
            input("\nPress Enter to continue...")
            
        elif choice == "5":
            # Exit
            print("\n👋 Goodbye!\n")
            sys.exit(0)
            
        else:
            print("\n❌ Invalid choice. Please enter 1, 2, 3, 4, or 5")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user. Goodbye!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("\n💡 Please report this issue if it persists")
        sys.exit(1)