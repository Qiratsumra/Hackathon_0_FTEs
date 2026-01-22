"""
Base Watcher Class for AI Employee System

Abstract base class that defines the interface for all watcher implementations.
Watchers monitor various input sources and create markdown task files in the
Needs_Action/ folder when new items are detected.

Author: AI Employee System
Created: 2026-01-22
"""

import os
import time
import logging
import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
import yaml
from typing import Dict, Any, Optional, Callable


class BaseWatcher(ABC):
    """
    Abstract base class for all watchers in the AI Employee system.

    Watchers continuously monitor input sources (files, emails, APIs, etc.)
    and create markdown task files in the Needs_Action/ folder when new items
    are detected that require processing.
    """

    def __init__(self, name: str, interval: int = 30, vault_path: str = "~/AI_Employee_Vault"):
        """
        Initialize the base watcher.

        Args:
            name (str): Name of the watcher for identification
            interval (int): Polling interval in seconds
            vault_path (str): Path to the Obsidian vault
        """
        self.name = name
        self.interval = interval
        self.vault_path = Path(vault_path).expanduser()
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.logs_path = self.vault_path / "Logs"
        self.is_running = False

        # Create necessary directories
        self.needs_action_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.setup_logging()

    def setup_logging(self):
        """Setup logging for the watcher."""
        log_filename = self.logs_path / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format=f'%(asctime)s - {self.name} - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler()  # Also log to console
            ]
        )
        self.logger = logging.getLogger(self.name)

    def create_task_file(self, title: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Create a markdown task file in the Needs_Action folder.

        Args:
            title (str): Title of the task
            content (str): Main content/body of the task
            metadata (dict, optional): YAML frontmatter metadata

        Returns:
            Path: Path to the created task file
        """
        if metadata is None:
            metadata = {}

        # Add creation timestamp and source
        metadata['created'] = datetime.now().isoformat()
        metadata['source'] = self.name
        metadata['status'] = 'new'
        metadata['priority'] = metadata.get('priority', 'medium')

        # Sanitize title for filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_').lower()[:100]  # Limit length

        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{safe_title}.md"
        filepath = self.needs_action_path / filename

        # Create markdown content with YAML frontmatter
        markdown_content = f"""---
{yaml.dump(metadata, default_flow_style=False)}
---

# {title}

{content}

## Instructions
Process this task according to the guidelines in Company_Handbook.md

## Created by
{self.name} at {datetime.now().isoformat()}
"""

        # Write the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        self.logger.info(f"Created task file: {filepath}")
        return filepath

    @abstractmethod
    async def check_for_new_items(self):
        """
        Abstract method to check for new items in the monitored source.
        Must be implemented by subclasses.

        Returns:
            list: List of new items to process
        """
        pass

    @abstractmethod
    def format_item_as_task(self, item: Any) -> tuple:
        """
        Abstract method to format an item as a task title and content.
        Must be implemented by subclasses.

        Args:
            item: The item to format

        Returns:
            tuple: (title, content, metadata) for the task file
        """
        pass

    async def exponential_backoff(self, attempt: int, max_wait: int = 300):
        """
        Implement exponential backoff for error recovery.

        Args:
            attempt (int): Current attempt number
            max_wait (int): Maximum wait time in seconds
        """
        wait_time = min(2 ** attempt + (attempt * 0.1), max_wait)
        self.logger.warning(f"Attempt {attempt}: Waiting {wait_time:.1f}s before retry...")
        await asyncio.sleep(wait_time)

    async def run_once(self):
        """Run a single cycle of checking for new items."""
        try:
            new_items = await self.check_for_new_items()

            if new_items:
                self.logger.info(f"Found {len(new_items)} new items")

                for item in new_items:
                    try:
                        title, content, metadata = self.format_item_as_task(item)
                        self.create_task_file(title, content, metadata)
                    except Exception as e:
                        self.logger.error(f"Failed to format item as task: {e}")
                        continue
            else:
                self.logger.debug("No new items found")

        except Exception as e:
            self.logger.error(f"Error in watcher cycle: {e}")
            raise

    async def run(self):
        """
        Main run loop for the watcher.
        Continuously monitors the source and creates task files as needed.
        """
        self.is_running = True
        self.logger.info(f"Starting {self.name} with {self.interval}s interval")

        attempt = 0
        max_attempts = 5  # Reset after successful cycle

        while self.is_running:
            try:
                await self.run_once()
                attempt = 0  # Reset attempts after successful cycle
                await asyncio.sleep(self.interval)

            except Exception as e:
                if attempt >= max_attempts:
                    self.logger.error(f"Max attempts reached, stopping {self.name}")
                    break

                self.logger.error(f"Error in {self.name}: {e}, attempting recovery...")
                await self.exponential_backoff(attempt)
                attempt += 1

        self.logger.info(f"Stopped {self.name}")

    def stop(self):
        """Stop the watcher."""
        self.is_running = False
        self.logger.info(f"Stopping {self.name}")


if __name__ == "__main__":
    # Example usage (won't work as BaseWatcher is abstract)
    print("This is the base watcher class. Implement a concrete subclass to use.")