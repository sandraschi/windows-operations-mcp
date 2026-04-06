import unittest
import tempfile
import shutil
import subprocess
from pathlib import Path
import sys

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parents[3]))

from windows_operations_mcp.tools.portmanteau.git_operations import git_operations

class TestGitPortmanteau(unittest.TestCase):
    """Test modern Git portmanteau operations."""

    def setUp(self):
        """Set up a fresh temporary directory for each test."""
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.test_dir)

    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_git_init_and_status(self):
        """Test initializing a repo and checking status."""
        # Init
        result = git_operations(action="init", repo_path=str(self.repo_path))
        self.assertTrue(result["success"], f"Init failed: {result.get('error')}")
        self.assertTrue((self.repo_path / ".git").exists())

        # Status (empty)
        result = git_operations(action="status", repo_path=str(self.repo_path))
        self.assertTrue(result["success"])
        self.assertFalse(result["data"]["has_changes"])

        # Add file
        test_file = self.repo_path / "test.txt"
        test_file.write_text("hello sota")
        
        # Status (untracked)
        result = git_operations(action="status", repo_path=str(self.repo_path))
        self.assertTrue(result["success"])
        self.assertTrue(result["data"]["has_changes"])
        self.assertIn("test.txt", result["data"]["changes"]["untracked"])

    def test_git_add_commit_log(self):
        """Test full add/commit/log workflow."""
        git_operations(action="init", repo_path=str(self.repo_path))
        
        # Configure user for the temporary repo to avoid commit failure
        subprocess.run(["git", "config", "user.email", "sota@example.com"], cwd=self.repo_path)
        subprocess.run(["git", "config", "user.name", "SOTA Agent"], cwd=self.repo_path)
        
        # Create and add
        (self.repo_path / "file1.txt").write_text("content 1")
        result = git_operations(action="add", repo_path=str(self.repo_path), all_files=True)
        self.assertTrue(result["success"])
        
        # Commit
        result = git_operations(action="commit", repo_path=str(self.repo_path), message="First commit")
        self.assertTrue(result["success"])
        
        # Log
        result = git_operations(action="log", repo_path=str(self.repo_path))
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["count"], 1)
        self.assertEqual(result["data"]["entries"][0]["subject"], "First commit")

    def test_git_status_complex_parsing(self):
        """Test parsing of staged vs unstaged changes."""
        git_operations(action="init", repo_path=str(self.repo_path))
        subprocess.run(["git", "config", "user.email", "sota@example.com"], cwd=self.repo_path)
        subprocess.run(["git", "config", "user.name", "SOTA Agent"], cwd=self.repo_path)
        
        # 1. Test AM (Added staged, Modified unstaged)
        f1 = self.repo_path / "am_test.txt"
        f1.write_text("initial")
        git_operations(action="add", repo_path=str(self.repo_path), files=["am_test.txt"])
        f1.write_text("modified")
        
        result = git_operations(action="status", repo_path=str(self.repo_path))
        changes = result["data"]["changes"]
        self.assertIn("(staged) am_test.txt", changes["added"])
        self.assertIn("am_test.txt", changes["modified"])

        # 2. Test MM (Modified staged, Modified unstaged)
        f2 = self.repo_path / "mm_test.txt"
        f2.write_text("v1")
        git_operations(action="add", repo_path=str(self.repo_path), files=["mm_test.txt"])
        git_operations(action="commit", repo_path=str(self.repo_path), message="commit f2")
        
        f2.write_text("v2")
        git_operations(action="add", repo_path=str(self.repo_path), files=["mm_test.txt"])
        f2.write_text("v3")
        
        result = git_operations(action="status", repo_path=str(self.repo_path))
        changes = result["data"]["changes"]
        self.assertIn("(staged) mm_test.txt", changes["modified"])
        self.assertIn("mm_test.txt", changes["modified"])
        
        # 3. Test Untracked
        (self.repo_path / "untracked.txt").write_text("untracked")
        result = git_operations(action="status", repo_path=str(self.repo_path))
        self.assertIn("untracked.txt", result["data"]["changes"]["untracked"])

    def test_error_non_repo(self):
        """Test that it correctly identifies a non-git directory."""
        # Use an empty directory that wasn't git init'd
        result = git_operations(action="status", repo_path=str(self.repo_path))
        self.assertFalse(result["success"])
        self.assertIn("Not a Git repository", result["error"])

if __name__ == "__main__":
    unittest.main()
