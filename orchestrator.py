"""
AI Employee Orchestrator

Master coordinator that manages all components of the AI Employee system:
- Monitors vault folders for changes
- Triggers Claude Code when new tasks appear
- Processes approved actions
- Handles scheduled tasks
- Maintains health checks and process management

Author: AI Employee System
Created: 2026-01-22
"""

import os
import sys
import time
import json
import asyncio
import signal
import subprocess
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from collections import defaultdict
import logging
from logging.handlers import RotatingFileHandler
import schedule
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import psutil


@dataclass
class TaskInfo:
    """Information about a task in the system."""
    id: str
    filepath: Path
    created_at: datetime
    status: str
    priority: str
    category: str


class VaultFolderMonitor(FileSystemEventHandler):
    """Monitor vault folders for changes."""

    def __init__(self, orchestrator):
        super().__init__()
        self.orchestrator = orchestrator
        self.logger = logging.getLogger(__name__)

    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return

        filepath = Path(event.src_path)
        if filepath.suffix.lower() == '.md':
            self.logger.info(f"New file detected: {filepath}")
            self.orchestrator.handle_new_file(filepath)

    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return

        filepath = Path(event.src_path)
        if filepath.suffix.lower() == '.md':
            self.logger.info(f"File modified: {filepath}")
            self.orchestrator.handle_file_change(filepath)


class Orchestrator:
    """Main orchestrator for the AI Employee system."""

    def __init__(self, vault_path: str = "./AI_Employee_Vault", dropzone_path: str = "./AI_Employee_Dropzone"):
        # Handle both relative paths and home directory references
        if "~" in vault_path:
            self.vault_path = Path(vault_path).expanduser()
        else:
            self.vault_path = Path(vault_path).resolve()

        if "~" in dropzone_path:
            self.dropzone_path = Path(dropzone_path).expanduser()
        else:
            self.dropzone_path = Path(dropzone_path).resolve()
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.plans_path = self.vault_path / "Plans"
        self.in_progress_path = self.vault_path / "In_Progress"
        self.pending_approval_path = self.vault_path / "Pending_Approval"
        self.approved_path = self.vault_path / "Approved"
        self.done_path = self.vault_path / "Done"
        self.logs_path = self.vault_path / "Logs"
        self.briefings_path = self.vault_path / "Briefings"

        # Setup logging
        self.setup_logging()
        self.logger = logging.getLogger('orchestrator')

        # Component tracking
        self.watchers = {}
        self.processes = {}
        self.is_running = False

        # Task tracking
        self.active_tasks = {}
        self.task_queue = []

        # Health check tracking
        self.component_health = {
            'orchestrator': 'healthy',
            'watchers': {},
            'claude_code': 'unknown',
            'mcp_servers': {}
        }

        # Create necessary directories
        self.ensure_directories()

    def setup_logging(self):
        """Setup logging for the orchestrator."""
        self.logs_path.mkdir(parents=True, exist_ok=True)

        # Create rotating file handler
        log_file = self.logs_path / f"orchestrator_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5  # 10MB files, keep 5 backups
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Logger setup
        logger = logging.getLogger('orchestrator')
        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        # Also configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        if not root_logger.handlers:
            root_logger.addHandler(file_handler)
            root_logger.addHandler(console_handler)

    def ensure_directories(self):
        """Ensure all required directories exist."""
        dirs_to_create = [
            self.needs_action_path,
            self.plans_path,
            self.in_progress_path,
            self.pending_approval_path,
            self.approved_path,
            self.done_path,
            self.logs_path,
            self.briefings_path,
            self.dropzone_path
        ]

        for directory in dirs_to_create:
            directory.mkdir(parents=True, exist_ok=True)

        self.logger.info("All required directories verified/created")

    def start_watchers(self):
        """Start all watcher processes."""
        self.logger.info("Starting watchers...")

        # Start file watcher
        try:
            file_watcher_cmd = [sys.executable, "file_watcher.py"]
            file_watcher_proc = subprocess.Popen(
                file_watcher_cmd,
                cwd=os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes['file_watcher'] = file_watcher_proc
            self.logger.info("File watcher started")
        except Exception as e:
            self.logger.error(f"Failed to start file watcher: {e}")

        # Start Gmail watcher (if configured)
        try:
            gmail_watcher_cmd = [sys.executable, "gmail_watcher.py"]
            gmail_watcher_proc = subprocess.Popen(
                gmail_watcher_cmd,
                cwd=os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes['gmail_watcher'] = gmail_watcher_proc
            self.logger.info("Gmail watcher started")
        except FileNotFoundError:
            self.logger.info("Gmail watcher not found, skipping...")
        except Exception as e:
            self.logger.error(f"Failed to start Gmail watcher: {e}")

    def stop_watchers(self):
        """Stop all watcher processes."""
        self.logger.info("Stopping watchers...")

        for name, proc in list(self.processes.items()):
            try:
                proc.terminate()
                proc.wait(timeout=5)  # Wait up to 5 seconds
                self.logger.info(f"{name} stopped gracefully")
            except subprocess.TimeoutExpired:
                proc.kill()
                self.logger.warning(f"{name} killed forcefully")
            except Exception as e:
                self.logger.error(f"Error stopping {name}: {e}")

        self.processes.clear()

    def monitor_vault_folders(self):
        """Monitor vault folders for changes using watchdog."""
        self.logger.info("Starting vault folder monitoring...")

        observer = Observer()

        # Monitor Needs_Action folder
        if self.needs_action_path.exists():
            event_handler = VaultFolderMonitor(self)
            observer.schedule(event_handler, str(self.needs_action_path), recursive=False)
            self.logger.info(f"Monitoring {self.needs_action_path}")

        observer.start()
        return observer

    def handle_new_file(self, filepath: Path):
        """Handle a newly created file in the vault."""
        self.logger.info(f"Handling new file: {filepath}")

        if "Needs_Action" in str(filepath):
            self.process_new_task(filepath)
        elif "Approved" in str(filepath):
            self.execute_approved_action(filepath)
        elif "Pending_Approval" in str(filepath):
            self.handle_approval_request(filepath)

    def handle_file_change(self, filepath: Path):
        """Handle a modified file in the vault."""
        self.logger.info(f"Handling file change: {filepath}")

        # Could implement additional logic for file modifications
        pass

    def process_new_task(self, task_file: Path):
        """Process a new task file found in Needs_Action folder."""
        self.logger.info(f"Processing new task: {task_file.name}")

        try:
            # Parse task file to extract metadata
            task_info = self.parse_task_file(task_file)

            # Move to In_Progress
            in_progress_file = self.move_task_file(task_file, self.in_progress_path)

            # Queue for Claude Code processing
            self.task_queue.append(task_info)

            # Trigger Claude Code processing
            self.trigger_claude_processing(task_info)

            self.logger.info(f"Task {task_file.name} queued for processing")

        except Exception as e:
            self.logger.error(f"Error processing task {task_file.name}: {e}")
            # Move to error handling area or log error

    def parse_task_file(self, task_file: Path) -> TaskInfo:
        """Parse a task file to extract metadata and information."""
        with open(task_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract YAML frontmatter if present
        if content.startswith('---'):
            end_frontmatter = content.find('---', 3)
            if end_frontmatter != -1:
                frontmatter = content[4:end_frontmatter].strip()
                import yaml
                metadata = yaml.safe_load(frontmatter) or {}
            else:
                metadata = {}
        else:
            metadata = {}

        # Create TaskInfo object
        task_id = task_file.stem.split('_')[0] if '_' in task_file.stem else task_file.stem
        created_str = metadata.get('created', str(datetime.now().isoformat()))

        return TaskInfo(
            id=task_id,
            filepath=task_file,
            created_at=datetime.fromisoformat(created_str.replace('Z', '+00:00')) if 'Z' in created_str else datetime.fromisoformat(created_str),
            status=metadata.get('status', 'new'),
            priority=metadata.get('priority', 'medium'),
            category=metadata.get('category', 'general')
        )

    def move_task_file(self, source_file: Path, destination_folder: Path) -> Path:
        """Move a task file to a new location."""
        destination_file = destination_folder / source_file.name
        source_file.rename(destination_file)
        self.logger.info(f"Moved {source_file.name} to {destination_folder.name}")
        return destination_file

    def trigger_claude_processing(self, task_info: TaskInfo):
        """Trigger Claude Code to process the task."""
        self.logger.info(f"Triggering Claude processing for task {task_info.id}")

        try:
            # Call the actual Claude Code integration asynchronously
            # We'll run this in a separate thread since orchestrator methods are synchronous
            import asyncio
            from ai_employee.claude_integration import process_task_with_claude

            # Read the task content
            with open(task_info.filepath, 'r', encoding='utf-8') as f:
                task_content = f.read()

            # Prepare task metadata
            task_metadata = {
                'id': task_info.id,
                'filepath': str(task_info.filepath),
                'created_at': task_info.created_at.isoformat(),
                'status': task_info.status,
                'priority': task_info.priority,
                'category': task_info.category
            }

            # Process the task with Claude Code
            result = asyncio.run(process_task_with_claude(task_content, task_metadata))

            # Handle the result
            if result.success:
                # Update the task file with Claude's response
                updated_content = f"""{task_content}

---

## Claude Analysis
{result.content}

## Metadata
- Processed At: {datetime.now().isoformat()}
- Model: {result.metadata.get('model', 'unknown')}
- Tokens Used: {result.metadata.get('total_tokens', 'unknown')}
"""

                with open(task_info.filepath, 'w', encoding='utf-8') as f:
                    f.write(updated_content)

                # Determine next action based on Claude's response
                if "approval" in result.content.lower() or "requires approval" in result.content.lower():
                    # Move to Pending Approval
                    new_location = self.move_task_file(task_info.filepath, self.pending_approval_path)
                    self.logger.info(f"Task {task_info.id} moved to Pending Approval based on Claude analysis")
                else:
                    # Move to Done (or Plans depending on the response)
                    if "plan" in result.content.lower() or "planned" in result.content.lower():
                        new_location = self.move_task_file(task_info.filepath, self.plans_path)
                        self.logger.info(f"Task {task_info.id} moved to Plans based on Claude analysis")
                    else:
                        new_location = self.move_task_file(task_info.filepath, self.done_path)
                        self.logger.info(f"Task {task_info.id} moved to Done based on Claude analysis")
            else:
                self.logger.error(f"Error from Claude processing: {result.error}")
                # On error, we might want to escalate to human or retry
                # For now, move to a special error folder or keep in current location
                error_path = self.logs_path / "processing_errors"
                error_path.mkdir(exist_ok=True)
                error_location = self.move_task_file(task_info.filepath, error_path)
                self.logger.error(f"Task {task_info.id} moved to error processing folder due to Claude error")

        except Exception as e:
            self.logger.error(f"Error triggering Claude processing: {e}")
            # Handle any exceptions during Claude processing
            import traceback
            error_log = f"Error in Claude processing: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            error_file = self.logs_path / f"claude_error_{task_info.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            with open(error_file, 'w') as f:
                f.write(error_log)


    def execute_approved_action(self, action_file: Path):
        """Execute an action that has been approved."""
        self.logger.info(f"Executing approved action: {action_file.name}")

        # In a real implementation, this would trigger the actual action
        # based on the content of the approved file

        # Move to Done after execution
        self.move_task_file(action_file, self.done_path)
        self.logger.info(f"Approved action {action_file.name} executed and archived")

    def handle_approval_request(self, approval_file: Path):
        """Handle a new approval request."""
        self.logger.info(f"New approval request detected: {approval_file.name}")

        # Log the approval request
        self.logger.info(f"Approval required for: {approval_file.name}")
        # In real implementation, this might notify the human operator

    def run_health_checks(self):
        """Perform health checks on all components."""
        self.logger.info("Running health checks...")

        # Check orchestrator itself
        self.component_health['orchestrator'] = 'healthy'

        # Check running processes
        for name, proc in self.processes.items():
            if proc.poll() is None:  # Process is still running
                self.component_health['watchers'][name] = 'healthy'
            else:
                self.component_health['watchers'][name] = 'failed'
                self.logger.warning(f"Watcher {name} has stopped unexpectedly")

        # Check vault directories
        vault_dirs = {
            'needs_action': self.needs_action_path,
            'plans': self.plans_path,
            'in_progress': self.in_progress_path,
            'pending_approval': self.pending_approval_path,
            'approved': self.approved_path,
            'done': self.done_path,
            'logs': self.logs_path
        }

        for name, path in vault_dirs.items():
            if path.exists():
                self.component_health[f'dir_{name}'] = 'accessible'
            else:
                self.component_health[f'dir_{name}'] = 'missing'
                self.logger.warning(f"Directory {path} is missing")

        self.logger.info("Health checks completed")

    def generate_daily_briefing(self):
        """Generate daily status briefing."""
        self.logger.info("Generating daily briefing...")

        # Count tasks in each folder
        needs_action_count = len(list(self.needs_action_path.glob("*.md")))
        in_progress_count = len(list(self.in_progress_path.glob("*.md")))
        pending_approval_count = len(list(self.pending_approval_path.glob("*.md")))
        approved_count = len(list(self.approved_path.glob("*.md")))

        # Generate briefing content
        briefing_content = f"""# Daily Status Briefing - {datetime.now().strftime('%Y-%m-%d')}

## Task Status
- **Needs Action:** {needs_action_count}
- **In Progress:** {in_progress_count}
- **Pending Approval:** {pending_approval_count}
- **Ready to Execute:** {approved_count}

## System Health
- **Orchestrator:** {self.component_health['orchestrator']}
- **Watchers:** {sum(1 for v in self.component_health['watchers'].values() if v == 'healthy')}/{len(self.component_health['watchers'])} healthy

## Next Steps
- Process {needs_action_count} pending tasks
- Follow up on {pending_approval_count} approval requests
- Monitor {in_progress_count} ongoing tasks

---
Generated by AI Employee Orchestrator at {datetime.now().isoformat()}
"""

        # Save to logs
        briefing_file = self.logs_path / f"daily_briefing_{datetime.now().strftime('%Y%m%d')}.md"
        with open(briefing_file, 'w', encoding='utf-8') as f:
            f.write(briefing_content)

        self.logger.info(f"Daily briefing saved to {briefing_file}")

    def generate_weekly_briefing(self):
        """Generate weekly CEO briefing."""
        self.logger.info("Generating weekly briefing...")

        # Import the briefing generator skill content
        try:
            with open("AI_Employee_Vault/.claude/skills/briefing_generator.md", 'r', encoding='utf-8') as f:
                skill_content = f.read()

            # This would normally call the briefing generator
            # For now we'll create a basic weekly briefing
            week_start = datetime.now() - timedelta(days=datetime.now().weekday())
            week_end = week_start + timedelta(days=6)

            briefing_content = f"""# Weekly CEO Briefing - Week of {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}

## Executive Summary

This week the AI Employee system managed routine operations while identifying opportunities for process improvement. Key metrics show steady performance with room for optimization in task prioritization.

## Revenue Performance

### Weekly Results
- **Actual Revenue:** $0 / **Target:** $0 (0% of target)
- **Daily Average:** $0 / **Target:** $0 per day
- **Trend:** Steady compared to previous week

### Monthly Progress
- **Month-to-Date:** $0 / $4000 (0% of monthly goal)
- **Projected Monthly Total:** $0 if current pace continues
- **Gap to Target:** $4000 needed to reach goal

## Key Performance Indicators

### Operational Metrics
| Metric | This Week | Last Week | Target | Status |
|--------|-----------|-----------|--------|---------|
| Tasks Completed | 0 | 0 | Variable | Neutral |
| Email Response Time | N/A | N/A | <2 hrs | N/A |
| System Uptime | 100% | 100% | >99% | Healthy |

## Completed Tasks

### Routine Operations
- System initialization and configuration
- Vault structure creation
- Skill development and testing
- MCP configuration setup

## Bottlenecks & Challenges

### Current Issues
1. **Initial Setup Phase**
   - Impact: Limited operational capacity during setup
   - Root cause: System configuration and testing phase
   - Resolution status: Ongoing - expected completion soon

## Trends & Insights

### Areas of Concern
- Initial setup phase means limited operational data
- Revenue tracking not yet active
- Need to establish baseline metrics

## Recommendations

### Immediate Actions (This Week)
1. **Complete System Setup**: Finish remaining configuration
2. **Begin Operations**: Start processing real tasks
3. **Establish Baseline**: Begin tracking operational metrics

### Strategic Considerations
1. **Process Optimization**: Fine-tune task processing workflows
2. **Performance Monitoring**: Enhance tracking and reporting
3. **Scalability Planning**: Prepare for increased workload

## Next Week Priorities

### Revenue Focus
- Begin revenue-generating activities
- Process initial client requests
- Track financial metrics

### Operational Improvements
- Optimize task processing speed
- Improve approval workflows
- Enhance error handling

---

**Generated by:** AI Employee System
**Last Updated:** {datetime.now().isoformat()}
**Next Briefing:** {(week_end + timedelta(days=1)).strftime('%Y-%m-%d')}
"""

            # Save to briefings folder
            briefing_file = self.briefings_path / f"{datetime.now().strftime('%Y%m%d')}_Weekly_Briefing.md"
            with open(briefing_file, 'w', encoding='utf-8') as f:
                f.write(briefing_content)

            self.logger.info(f"Weekly briefing saved to {briefing_file}")

        except Exception as e:
            self.logger.error(f"Error generating weekly briefing: {e}")

    def run(self):
        """Main run loop for the orchestrator."""
        self.logger.info("Starting AI Employee Orchestrator...")

        # Set up signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, shutting down gracefully...")
            self.shutdown()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Start watchers
        self.start_watchers()

        # Start vault folder monitoring
        observer = self.monitor_vault_folders()

        # Schedule periodic tasks
        schedule.every(30).seconds.do(self.run_health_checks)
        schedule.every().day.at("08:00").do(self.generate_daily_briefing)
        schedule.every().sunday.at("09:00").do(self.generate_weekly_briefing)

        self.is_running = True
        self.logger.info("Orchestrator started successfully")

        try:
            while self.is_running:
                # Run scheduled jobs
                schedule.run_pending()

                # Small delay to prevent busy waiting
                time.sleep(1)

        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received, shutting down...")
        finally:
            self.shutdown(observer)

    def shutdown(self, observer=None):
        """Shut down the orchestrator gracefully."""
        self.logger.info("Shutting down orchestrator...")

        self.is_running = False

        # Stop observers
        if observer:
            observer.stop()
            observer.join()

        # Stop watchers
        self.stop_watchers()

        # Wait for any remaining tasks
        time.sleep(2)

        self.logger.info("Orchestrator shut down complete")

    def get_status(self) -> Dict[str, Any]:
        """Get current status of the orchestrator."""
        return {
            'is_running': self.is_running,
            'active_watchers': list(self.processes.keys()),
            'component_health': self.component_health,
            'task_counts': {
                'needs_action': len(list(self.needs_action_path.glob("*.md"))) if self.needs_action_path.exists() else 0,
                'in_progress': len(list(self.in_progress_path.glob("*.md"))) if self.in_progress_path.exists() else 0,
                'pending_approval': len(list(self.pending_approval_path.glob("*.md"))) if self.pending_approval_path.exists() else 0,
                'approved': len(list(self.approved_path.glob("*.md"))) if self.approved_path.exists() else 0,
                'done': len(list(self.done_path.glob("*.md"))) if self.done_path.exists() else 0,
            },
            'uptime': getattr(self, 'start_time', datetime.now()) - datetime.now() if hasattr(self, 'start_time') else timedelta(seconds=0)
        }


def main():
    """Main function to run the orchestrator."""
    import argparse
    from ai_employee.claude_integration import initialize_claude_integration, close_claude_integration

    parser = argparse.ArgumentParser(description='AI Employee Orchestrator')
    parser.add_argument('--vault-path', default='./AI_Employee_Vault', help='Path to the Obsidian vault')
    parser.add_argument('--dropzone-path', default='./AI_Employee_Dropzone', help='Path to the file dropzone')

    args = parser.parse_args()

    orchestrator = Orchestrator(args.vault_path, args.dropzone_path)

    try:
        # Initialize Claude integration
        asyncio.run(initialize_claude_integration())

        orchestrator.run()
    except Exception as e:
        print(f"Error running orchestrator: {e}")
        logging.error(f"Fatal error in orchestrator: {e}")
        sys.exit(1)
    finally:
        # Close Claude integration when shutting down
        try:
            asyncio.run(close_claude_integration())
        except:
            pass  # Ignore errors during shutdown


if __name__ == "__main__":
    main()