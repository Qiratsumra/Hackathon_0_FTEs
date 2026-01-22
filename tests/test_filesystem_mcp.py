"""
Unit tests for the filesystem MCP module.
"""
import unittest
import tempfile
import shutil
from pathlib import Path
import asyncio
from ai_employee.filesystem_mcp import FilesystemMCP


class TestFilesystemMCP(unittest.TestCase):
    def setUp(self):
        self.mcp = FilesystemMCP()
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_read_file_success(self):
        """Test successful file reading."""
        test_file = self.test_dir / "test.txt"
        test_file.write_text("Hello, World!")

        async def run_test():
            result = await self.mcp.read_file({"path": str(test_file)})
            return result

        result = asyncio.run(run_test())

        self.assertIn("result", result)
        self.assertIn("content", result["result"])
        self.assertEqual(result["result"]["content"], "Hello, World!")

    def test_read_file_not_found(self):
        """Test reading a non-existent file."""
        async def run_test():
            result = await self.mcp.read_file({"path": str(self.test_dir / "nonexistent.txt")})
            return result

        result = asyncio.run(run_test())

        self.assertIn("error", result)

    def test_write_file_success(self):
        """Test successful file writing."""
        test_file = self.test_dir / "write_test.txt"
        content = "Test content for writing"

        async def run_test():
            result = await self.mcp.write_file({"path": str(test_file), "content": content})
            return result

        result = asyncio.run(run_test())

        self.assertIn("result", result)
        self.assertTrue(result["result"]["success"])
        self.assertTrue(test_file.exists())
        self.assertEqual(test_file.read_text(), content)

    def test_list_directory(self):
        """Test listing directory contents."""
        # Create test files
        (self.test_dir / "file1.txt").write_text("content1")
        (self.test_dir / "file2.txt").write_text("content2")

        async def run_test():
            result = await self.mcp.list_directory({"path": str(self.test_dir)})
            return result

        result = asyncio.run(run_test())

        self.assertIn("result", result)
        self.assertIn("files", result["result"])
        filenames = [f["name"] for f in result["result"]["files"]]
        self.assertIn("file1.txt", filenames)
        self.assertIn("file2.txt", filenames)

    def test_create_directory(self):
        """Test creating a directory."""
        new_dir = self.test_dir / "new_directory"

        async def run_test():
            result = await self.mcp.create_directory({"path": str(new_dir)})
            return result

        result = asyncio.run(run_test())

        self.assertIn("result", result)
        self.assertTrue(result["result"]["success"])
        self.assertTrue(new_dir.exists())
        self.assertTrue(new_dir.is_dir())


if __name__ == '__main__':
    unittest.main()