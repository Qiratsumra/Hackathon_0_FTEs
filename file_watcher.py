"""
File Watcher for AI Employee System

Monitors a designated dropzone folder for new files and creates task files
in the Needs_Action/ folder when new files are detected.

Author: AI Employee System
Created: 2026-01-22
"""

import os
import time
import asyncio
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict, Any
import mimetypes

from base_watcher import BaseWatcher


class FileWatcher(BaseWatcher):
    """
    File watcher that monitors a dropzone folder for new files.

    Creates markdown task files in Needs_Action/ when new files are detected.
    """

    def __init__(self,
                 dropzone_path: str = "~/AI_Employee_Dropzone",
                 interval: int = 10,
                 vault_path: str = "~/AI_Employee_Vault",
                 supported_types: List[str] = None):
        """
        Initialize the file watcher.

        Args:
            dropzone_path (str): Path to monitor for new files
            interval (int): Polling interval in seconds
            vault_path (str): Path to the Obsidian vault
            supported_types (list): List of supported file extensions
        """
        super().__init__("FileWatcher", interval, vault_path)

        self.dropzone_path = Path(dropzone_path).expanduser()
        self.dropzone_path.mkdir(parents=True, exist_ok=True)

        # Track seen files to avoid duplicates
        self.seen_files = set()
        self.load_seen_files()

        # Supported file types
        self.supported_types = supported_types or [
            '.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx',
            '.csv', '.jpg', '.jpeg', '.png', '.gif', '.mp4',
            '.mp3', '.wav', '.zip', '.rar', '.eml', '.msg'
        ]

        self.logger.info(f"Initialized FileWatcher")
        self.logger.info(f"Monitoring: {self.dropzone_path}")
        self.logger.info(f"Supported types: {self.supported_types}")

    def load_seen_files(self):
        """Load previously seen files from a tracking file."""
        tracking_file = self.logs_path / "seen_files.txt"
        if tracking_file.exists():
            try:
                with open(tracking_file, 'r') as f:
                    self.seen_files = set(line.strip() for line in f if line.strip())
            except Exception as e:
                self.logger.error(f"Failed to load seen files: {e}")

    def save_seen_files(self):
        """Save seen files to tracking file."""
        tracking_file = self.logs_path / "seen_files.txt"
        try:
            with open(tracking_file, 'w') as f:
                for file_hash in self.seen_files:
                    f.write(f"{file_hash}\n")
        except Exception as e:
            self.logger.error(f"Failed to save seen files: {e}")

    def get_file_hash(self, filepath: Path) -> str:
        """
        Generate a hash for the file based on path and modification time.

        Args:
            filepath (Path): Path to the file

        Returns:
            str: Hash of the file
        """
        stat = filepath.stat()
        file_info = f"{filepath}_{stat.st_mtime}_{stat.st_size}"
        return hashlib.md5(file_info.encode()).hexdigest()

    def get_files_to_process(self) -> List[Path]:
        """
        Get list of new files to process.

        Returns:
            list: List of file paths to process
        """
        files_to_process = []

        for file_path in self.dropzone_path.rglob("*"):
            if file_path.is_file():
                # Check if file type is supported
                if file_path.suffix.lower() in self.supported_types:
                    file_hash = self.get_file_hash(file_path)

                    # Only process if we haven't seen this file before
                    if file_hash not in self.seen_files:
                        files_to_process.append(file_path)
                        self.seen_files.add(file_hash)

        return files_to_process

    async def check_for_new_items(self) -> List[Path]:
        """
        Check for new files in the dropzone folder.

        Returns:
            list: List of new file paths to process
        """
        try:
            new_files = self.get_files_to_process()

            # Save seen files periodically
            if len(self.seen_files) % 10 == 0:  # Every 10 new files
                self.save_seen_files()

            return new_files

        except Exception as e:
            self.logger.error(f"Error checking for new files: {e}")
            return []

    def format_item_as_task(self, file_path: Path) -> Tuple[str, str, Dict[str, Any]]:
        """
        Format a file as a task title and content.

        Args:
            file_path (Path): Path to the file

        Returns:
            tuple: (title, content, metadata) for the task file
        """
        # Determine file type and priority
        file_ext = file_path.suffix.lower()

        # Set priority based on file type
        priority_map = {
            '.pdf': 'high',
            '.doc': 'medium',
            '.docx': 'medium',
            '.xls': 'high',
            '.xlsx': 'high',
            '.csv': 'high',
            '.eml': 'high',
            '.msg': 'high'
        }

        priority = priority_map.get(file_ext, 'medium')

        # Determine file category
        category_map = {
            '.pdf': 'Document',
            '.doc': 'Document',
            '.docx': 'Document',
            '.xls': 'Spreadsheet',
            '.xlsx': 'Spreadsheet',
            '.csv': 'Data',
            '.txt': 'Text',
            '.jpg': 'Image',
            '.jpeg': 'Image',
            '.png': 'Image',
            '.gif': 'Image',
            '.mp4': 'Video',
            '.mp3': 'Audio',
            '.wav': 'Audio',
            '.zip': 'Archive',
            '.rar': 'Archive',
            '.eml': 'Email',
            '.msg': 'Email'
        }

        category = category_map.get(file_ext, 'Unknown')

        # Create title
        title = f"Process File: {file_path.name}"

        # Create content
        file_size = file_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)

        content = f"""## File Details
- **Name:** {file_path.name}
- **Path:** {file_path}
- **Size:** {file_size_mb:.2f} MB
- **Type:** {category} ({file_ext})
- **Modified:** {datetime.fromtimestamp(file_path.stat().st_mtime)}

## File Location
The file is located in the dropzone folder and requires processing.

## Processing Instructions
1. Review the file content
2. Determine appropriate action based on file type
3. Follow procedures outlined in Company_Handbook.md
4. Update status in task management system

## File Preview
```
File: {file_path.name}
Size: {file_size} bytes
Location: {file_path.parent}
```
"""

        # Create metadata
        metadata = {
            'priority': priority,
            'category': category,
            'file_type': file_ext,
            'file_size': file_size,
            'file_path': str(file_path),
            'action_required': 'review'
        }

        return title, content, metadata

    def cleanup_old_seen_files(self):
        """
        Remove hashes of files that no longer exist in the dropzone.
        """
        try:
            current_files = set()
            for file_path in self.dropzone_path.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in self.supported_types:
                    file_hash = self.get_file_hash(file_path)
                    current_files.add(file_hash)

            # Remove hashes for files that no longer exist
            files_to_remove = self.seen_files - current_files
            self.seen_files = current_files

            if files_to_remove:
                self.logger.info(f"Removed {len(files_to_remove)} old file hashes")

        except Exception as e:
            self.logger.error(f"Error cleaning up old seen files: {e}")


async def main():
    """
    Main function to run the file watcher.
    """
    # Create file watcher instance
    watcher = FileWatcher(
        dropzone_path="./AI_Employee_Dropzone",
        interval=10,  # Check every 10 seconds
        vault_path="./AI_Employee_Vault"
    )

    try:
        print(f"Starting FileWatcher...")
        print(f"Monitoring: {watcher.dropzone_path}")
        print(f"Output to: {watcher.needs_action_path}")
        print("Press Ctrl+C to stop")

        await watcher.run()

    except KeyboardInterrupt:
        print("\nStopping FileWatcher...")
        watcher.stop()

        # Save seen files before exiting
        watcher.save_seen_files()

    except Exception as e:
        print(f"Error running FileWatcher: {e}")
        watcher.logger.error(f"Fatal error: {e}")


if __name__ == "__main__":
    asyncio.run(main())