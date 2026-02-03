"""
WhatsApp Watcher - Monitors WhatsApp Web for important messages
Extends base_watcher.py pattern used in Gmail watcher
"""
import time
import logging
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import json
import re
import sys
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class BaseWatcher(ABC):
    """Base class for all watchers (if not already imported)"""
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        
    @abstractmethod
    def check_for_updates(self) -> list:
        '''Return list of new items to process'''
        pass
    
    @abstractmethod
    def create_action_file(self, item) -> Path:
        '''Create .md file in Needs_Action folder'''
        pass
    
    def run(self):
        self.logger.info(f'Starting {self.__class__.__name__}')
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    self.create_action_file(item)
            except Exception as e:
                self.logger.error(f'Error: {e}')
            time.sleep(self.check_interval)


class WhatsAppWatcher(BaseWatcher):
    def __init__(
        self,
        vault_path: str,
        session_path: str = "./whatsapp_session",
        check_interval: int = 30,
        keywords: list = None
    ):
        """
        Initialize WhatsApp Watcher
        
        Args:
            vault_path: Path to Obsidian vault
            session_path: Path to saved WhatsApp session
            check_interval: Seconds between checks
            keywords: List of keywords that trigger action (None = all messages)
        """
        super().__init__(vault_path, check_interval)
        self.session_path = Path(session_path)
        self.keywords = keywords or [
            'urgent', 'asap', 'help', 'invoice', 'payment', 
            'order', 'question', 'problem', 'issue', 'quote',
            'price', 'buy', 'purchase', 'interested'
        ]
        self.processed_ids = set()
        self._load_processed_ids()
        
    def _load_processed_ids(self):
        """Load processed message IDs from file"""
        logs_dir = self.vault_path / 'Logs'
        logs_dir.mkdir(exist_ok=True)
        processed_file = logs_dir / 'whatsapp_processed.json'
        
        if processed_file.exists():
            try:
                with open(processed_file, 'r') as f:
                    data = json.load(f)
                    self.processed_ids = set(data.get('processed_ids', []))
                self.logger.info(f"Loaded {len(self.processed_ids)} processed message IDs")
            except Exception as e:
                self.logger.error(f"Error loading processed IDs: {e}")
    
    def _save_processed_ids(self):
        """Save processed message IDs to file"""
        logs_dir = self.vault_path / 'Logs'
        logs_dir.mkdir(exist_ok=True)
        processed_file = logs_dir / 'whatsapp_processed.json'
        
        try:
            with open(processed_file, 'w') as f:
                json.dump({
                    'processed_ids': list(self.processed_ids),
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving processed IDs: {e}")
    
    def check_for_updates(self) -> list:
        """
        Check WhatsApp Web for new messages matching keywords
        Returns list of message objects
        """
        messages = []
        
        try:
            with sync_playwright() as p:
                # Launch browser with saved session
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=True,
                    args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto('https://web.whatsapp.com', wait_until='domcontentloaded')
                
                # Wait for WhatsApp to load
                try:
                    page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
                except PlaywrightTimeout:
                    self.logger.error("WhatsApp didn't load. Session may have expired.")
                    browser.close()
                    return messages
                
                # Find unread chats
                unread_chats = page.query_selector_all('[aria-label*="unread message"]')
                
                self.logger.info(f"Found {len(unread_chats)} unread chats")
                
                for chat in unread_chats[:10]:  # Process max 10 chats per check
                    try:
                        # Click on chat to open
                        chat.click()
                        time.sleep(1)  # Wait for chat to load
                        
                        # Get contact name
                        contact_elem = page.query_selector('[data-testid="conversation-header"]')
                        contact_name = contact_elem.inner_text().split('\n')[0] if contact_elem else "Unknown"
                        
                        # Get all unread messages in this chat
                        message_elems = page.query_selector_all('[data-testid="msg-container"]')
                        
                        for msg_elem in message_elems[-5:]:  # Check last 5 messages
                            try:
                                # Get message text
                                text_elem = msg_elem.query_selector('[class*="copyable-text"]')
                                if not text_elem:
                                    continue
                                
                                message_text = text_elem.inner_text()
                                
                                # Create unique ID for message
                                message_id = f"{contact_name}_{hash(message_text)}_{datetime.now().strftime('%Y%m%d')}"
                                
                                # Skip if already processed
                                if message_id in self.processed_ids:
                                    continue
                                
                                # Check if message matches any keyword
                                message_lower = message_text.lower()
                                matched_keywords = [kw for kw in self.keywords if kw in message_lower]
                                
                                if matched_keywords or len(self.keywords) == 0:
                                    messages.append({
                                        'id': message_id,
                                        'contact': contact_name,
                                        'text': message_text,
                                        'keywords': matched_keywords,
                                        'timestamp': datetime.now().isoformat()
                                    })
                                    self.processed_ids.add(message_id)
                                    self.logger.info(f"New message from {contact_name}: {message_text[:50]}...")
                                
                            except Exception as e:
                                self.logger.error(f"Error processing message: {e}")
                                continue
                    
                    except Exception as e:
                        self.logger.error(f"Error processing chat: {e}")
                        continue
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f"Error checking WhatsApp: {e}")
        
        # Save processed IDs
        if messages:
            self._save_processed_ids()
        
        return messages
    
    def create_action_file(self, message: dict) -> Path:
        """
        Create action file in Needs_Action folder
        
        Args:
            message: Message dict with id, contact, text, keywords
        
        Returns:
            Path to created file
        """
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        contact_safe = re.sub(r'[^a-zA-Z0-9_]', '_', message['contact'])
        filename = f'WHATSAPP_{contact_safe}_{timestamp}.md'
        filepath = self.needs_action / filename
        
        # Priority based on keywords
        priority = 'high' if any(kw in ['urgent', 'asap', 'help', 'problem'] for kw in message.get('keywords', [])) else 'medium'
        
        # Create markdown content
        content = f"""---
type: whatsapp
contact: {message['contact']}
received: {message['timestamp']}
priority: {priority}
status: pending
keywords: {', '.join(message.get('keywords', []))}
message_id: {message['id']}
---

## WhatsApp Message

**From:** {message['contact']}  
**Received:** {message['timestamp']}  
**Priority:** {priority}

### Message Content

{message['text']}

### Suggested Actions

- [ ] Read and understand the message
- [ ] Determine appropriate response
- [ ] Draft reply (check Company_Handbook.md for tone guidelines)
- [ ] If sensitive: Create approval request in /Pending_Approval
- [ ] If auto-approved: Send via WhatsApp MCP
- [ ] Log action in /Logs

### Context

Keywords detected: {', '.join(message.get('keywords', ['none']))}

### Notes

Add any additional context or instructions here.
"""
        
        # Write file
        filepath.write_text(content)
        self.logger.info(f"Created action file: {filename}")
        
        return filepath

def main():
    """Run WhatsApp watcher standalone"""
    import os
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    vault_path = os.getenv('OBSIDIAN_VAULT_PATH', './AI_Employee_Vault')
    session_path = os.getenv('WHATSAPP_SESSION_PATH', './whatsapp_session')
    
    watcher = WhatsAppWatcher(
        vault_path=vault_path,
        session_path=session_path,
        check_interval=30
    )
    
    print("🚀 Starting WhatsApp Watcher...")
    print(f"📂 Vault: {vault_path}")
    print(f"🔐 Session: {session_path}")
    print(f"🔍 Keywords: {', '.join(watcher.keywords)}")
    print("="*60)
    print("\nPress Ctrl+C to stop\n")
    
    try:
        watcher.run()
    except KeyboardInterrupt:
        print("\n\n👋 Stopping WhatsApp Watcher...")
        sys.exit(0)

if __name__ == "__main__":
    main()