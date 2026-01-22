"""
Unit tests for the orchestrator module.
"""
import unittest
import asyncio
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from orchestrator import Orchestrator, TaskInfo


class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        # Create temporary directories for testing
        self.test_dir = Path(tempfile.mkdtemp())
        self.vault_path = self.test_dir / "test_vault"
        self.dropzone_path = self.test_dir / "test_dropzone"

        # Initialize orchestrator with test paths
        self.orchestrator = Orchestrator(
            vault_path=str(self.vault_path),
            dropzone_path=str(self.dropzone_path)
        )

    def tearDown(self):
        # Clean up temporary directories
        shutil.rmtree(self.test_dir)

    def test_initialization(self):
        """Test orchestrator initialization."""
        self.assertTrue(self.vault_path.exists())
        self.assertTrue(self.dropzone_path.exists())
        self.assertEqual(self.orchestrator.vault_path, self.vault_path.resolve())
        self.assertEqual(self.orchestrator.dropzone_path, self.dropzone_path.resolve())

    def test_parse_task_file(self):
        """Test parsing a task file with YAML frontmatter."""
        # Create a test task file with YAML frontmatter
        task_file = self.vault_path / "Needs_Action" / "test_task.md"
        task_file.parent.mkdir(parents=True, exist_ok=True)

        content = """---
id: test123
created: '2026-01-22T12:00:00'
status: new
priority: medium
category: general
---

# Test Task

This is a test task for validation.
"""
        task_file.write_text(content)

        task_info = self.orchestrator.parse_task_file(task_file)

        self.assertIsInstance(task_info, TaskInfo)
        self.assertEqual(task_info.id, "test123")
        self.assertEqual(task_info.status, "new")
        self.assertEqual(task_info.priority, "medium")
        self.assertEqual(task_info.category, "general")

    def test_move_task_file(self):
        """Test moving a task file between folders."""
        # Create source and destination files
        source_file = self.vault_path / "Needs_Action" / "test_task.md"
        source_file.parent.mkdir(parents=True, exist_ok=True)
        source_file.write_text("Test content")

        # Move to In_Progress
        destination_file = self.orchestrator.move_task_file(source_file, self.vault_path / "In_Progress")

        # Check that file was moved
        self.assertFalse(source_file.exists())
        self.assertTrue(destination_file.exists())
        self.assertIn("test_task.md", destination_file.name)

    def test_task_info_creation(self):
        """Test creating TaskInfo objects."""
        task_id = "test123"
        filepath = self.vault_path / "test_task.md"
        created_at = datetime.now()
        status = "new"
        priority = "high"
        category = "email"

        task_info = TaskInfo(
            id=task_id,
            filepath=filepath,
            created_at=created_at,
            status=status,
            priority=priority,
            category=category
        )

        self.assertEqual(task_info.id, task_id)
        self.assertEqual(task_info.filepath, filepath)
        self.assertEqual(task_info.created_at, created_at)
        self.assertEqual(task_info.status, status)
        self.assertEqual(task_info.priority, priority)
        self.assertEqual(task_info.category, category)


if __name__ == '__main__':
    unittest.main()