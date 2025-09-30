import unittest
import tempfile
import os
import zipfile
import tarfile
from pathlib import Path
import sys

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.windows_operations_mcp.tools.archive_tools import (
    create_archive,
    extract_archive,
    list_archive,
    _get_archive_format,
    _should_exclude_path,
    UnsupportedFormatError
)


class TestArchiveTools(unittest.TestCase):
    """Test archive tools functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_files = []
        
        # Create test files
        for i in range(5):
            test_file = Path(self.test_dir) / f"test_file_{i}.txt"
            test_file.write_text(f"Test content {i}")
            self.test_files.append(str(test_file))
        
        # Create test subdirectory with files
        self.test_subdir = Path(self.test_dir) / "subdir"
        self.test_subdir.mkdir()
        for i in range(3):
            test_file = self.test_subdir / f"sub_file_{i}.txt"
            test_file.write_text(f"Subdir content {i}")

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # ========== Format Detection Tests ==========
    
    def test_get_archive_format_zip(self):
        """Test ZIP format detection."""
        self.assertEqual(_get_archive_format("test.zip"), "zip")
        self.assertEqual(_get_archive_format("TEST.ZIP"), "zip")
        self.assertEqual(_get_archive_format("/path/to/archive.zip"), "zip")

    def test_get_archive_format_tar(self):
        """Test TAR format detection."""
        self.assertEqual(_get_archive_format("test.tar"), "tar")
        self.assertEqual(_get_archive_format("TEST.TAR"), "tar")

    def test_get_archive_format_tar_gz(self):
        """Test TAR.GZ format detection."""
        self.assertEqual(_get_archive_format("test.tar.gz"), "tar.gz")
        self.assertEqual(_get_archive_format("test.tgz"), "tar.gz")
        self.assertEqual(_get_archive_format("TEST.TAR.GZ"), "tar.gz")

    def test_get_archive_format_unsupported(self):
        """Test unsupported format raises error."""
        with self.assertRaises(UnsupportedFormatError):
            _get_archive_format("test.rar")
        with self.assertRaises(UnsupportedFormatError):
            _get_archive_format("test.7z")

    # ========== Exclusion Pattern Tests ==========
    
    def test_should_exclude_path_simple_pattern(self):
        """Test simple exclusion patterns."""
        self.assertTrue(_should_exclude_path("test.log", ["*.log"]))
        self.assertFalse(_should_exclude_path("test.txt", ["*.log"]))

    def test_should_exclude_path_multiple_patterns(self):
        """Test multiple exclusion patterns."""
        patterns = ["*.log", "*.tmp", "*.cache"]
        self.assertTrue(_should_exclude_path("debug.log", patterns))
        self.assertTrue(_should_exclude_path("temp.tmp", patterns))
        self.assertFalse(_should_exclude_path("data.txt", patterns))

    def test_should_exclude_path_directory_pattern(self):
        """Test directory exclusion patterns."""
        patterns = ["__pycache__", ".git"]
        self.assertTrue(_should_exclude_path("__pycache__/module.pyc", patterns))
        self.assertTrue(_should_exclude_path(".git/config", patterns))
        self.assertFalse(_should_exclude_path("src/module.py", patterns))

    # ========== ZIP Archive Tests ==========
    
    def test_create_zip_archive_basic(self):
        """Test creating a basic ZIP archive."""
        archive_path = Path(self.test_dir) / "test.zip"
        
        result = create_archive(
            archive_path=str(archive_path),
            source_paths=[self.test_files[0]],
            use_default_exclusions=False,
            use_gitignore=False
        )
        
        self.assertTrue(result['success'])
        self.assertTrue(archive_path.exists())
        self.assertGreater(result['included_count'], 0)
        
        # Verify archive contents
        with zipfile.ZipFile(archive_path, 'r') as zf:
            self.assertGreater(len(zf.namelist()), 0)

    def test_create_zip_archive_multiple_files(self):
        """Test creating ZIP archive with multiple files."""
        archive_path = Path(self.test_dir) / "multi.zip"
        
        result = create_archive(
            archive_path=str(archive_path),
            source_paths=self.test_files[:3],
            compression_level=6,
            use_default_exclusions=False,
            use_gitignore=False
        )
        
        self.assertTrue(result['success'])
        self.assertTrue(archive_path.exists())
        self.assertEqual(result['included_count'], 3)

    def test_create_zip_archive_with_directory(self):
        """Test creating ZIP archive with directory."""
        archive_path = Path(self.test_dir) / "dir.zip"
        
        result = create_archive(
            archive_path=str(archive_path),
            source_paths=[self.test_dir],
            use_default_exclusions=False,
            use_gitignore=False
        )
        
        self.assertTrue(result['success'])
        self.assertTrue(archive_path.exists())
        self.assertGreater(result['included_count'], 0)

    def test_create_zip_archive_with_exclusions(self):
        """Test creating ZIP archive with exclusion patterns."""
        # Create files to exclude
        log_file = Path(self.test_dir) / "debug.log"
        log_file.write_text("Log content")
        
        archive_path = Path(self.test_dir) / "excluded.zip"
        
        result = create_archive(
            archive_path=str(archive_path),
            source_paths=[self.test_dir],
            exclude_patterns=["*.log", "*.zip"],
            use_default_exclusions=False,
            use_gitignore=False
        )
        
        self.assertTrue(result['success'])
        self.assertGreater(result['excluded_count'], 0)
        
        # Verify log file was excluded
        with zipfile.ZipFile(archive_path, 'r') as zf:
            names = zf.namelist()
            self.assertNotIn("debug.log", [os.path.basename(n) for n in names])

    def test_create_zip_archive_compression_levels(self):
        """Test creating ZIP archives with different compression levels."""
        for level in [0, 5, 9]:
            archive_path = Path(self.test_dir) / f"compress_{level}.zip"
            
            result = create_archive(
                archive_path=str(archive_path),
                source_paths=[self.test_files[0]],
                compression_level=level,
                use_default_exclusions=False,
                use_gitignore=False
            )
            
            self.assertTrue(result['success'])
            self.assertTrue(archive_path.exists())

    # ========== TAR Archive Tests ==========
    
    def test_create_tar_archive_basic(self):
        """Test creating a basic TAR archive."""
        archive_path = Path(self.test_dir) / "test.tar"
        
        result = create_archive(
            archive_path=str(archive_path),
            source_paths=[self.test_files[0]],
            use_default_exclusions=False,
            use_gitignore=False
        )
        
        self.assertTrue(result['success'])
        self.assertTrue(archive_path.exists())
        
        # Verify archive contents
        with tarfile.open(archive_path, 'r') as tf:
            self.assertGreater(len(tf.getnames()), 0)

    def test_create_tar_gz_archive(self):
        """Test creating a TAR.GZ archive."""
        archive_path = Path(self.test_dir) / "test.tar.gz"
        
        result = create_archive(
            archive_path=str(archive_path),
            source_paths=[self.test_files[0]],
            use_default_exclusions=False,
            use_gitignore=False
        )
        
        self.assertTrue(result['success'])
        self.assertTrue(archive_path.exists())
        
        # Verify archive contents
        with tarfile.open(archive_path, 'r:gz') as tf:
            self.assertGreater(len(tf.getnames()), 0)

    # ========== Extract Archive Tests ==========
    
    def test_extract_zip_archive(self):
        """Test extracting a ZIP archive."""
        # Create archive
        archive_path = Path(self.test_dir) / "extract_test.zip"
        create_archive(
            archive_path=str(archive_path),
            source_paths=self.test_files[:2],
            use_default_exclusions=False,
            use_gitignore=False
        )
        
        # Extract archive
        extract_dir = Path(self.test_dir) / "extracted"
        result = extract_archive(
            archive_path=str(archive_path),
            extract_dir=str(extract_dir)
        )
        
        self.assertTrue(result['success'])
        self.assertTrue(extract_dir.exists())
        self.assertGreater(len(result['extracted_files']), 0)

    def test_extract_zip_archive_specific_members(self):
        """Test extracting specific files from ZIP archive."""
        # Create archive with multiple files
        archive_path = Path(self.test_dir) / "members_test.zip"
        create_archive(
            archive_path=str(archive_path),
            source_paths=self.test_files,
            use_default_exclusions=False,
            use_gitignore=False
        )
        
        # Extract only specific file
        extract_dir = Path(self.test_dir) / "members_extracted"
        
        # First, list archive to get exact member names
        list_result = list_archive(archive_path=str(archive_path))
        self.assertTrue(list_result['success'])
        
        if list_result['files']:
            # Extract first file only
            result = extract_archive(
                archive_path=str(archive_path),
                extract_dir=str(extract_dir),
                members=[list_result['files'][0]]
            )
            
            self.assertTrue(result['success'])
            self.assertEqual(len(result['extracted_files']), 1)

    def test_extract_tar_archive(self):
        """Test extracting a TAR archive."""
        # Create archive
        archive_path = Path(self.test_dir) / "extract_test.tar"
        create_archive(
            archive_path=str(archive_path),
            source_paths=self.test_files[:2],
            use_default_exclusions=False,
            use_gitignore=False
        )
        
        # Extract archive
        extract_dir = Path(self.test_dir) / "tar_extracted"
        result = extract_archive(
            archive_path=str(archive_path),
            extract_dir=str(extract_dir)
        )
        
        self.assertTrue(result['success'])
        self.assertTrue(extract_dir.exists())

    def test_extract_tar_gz_archive(self):
        """Test extracting a TAR.GZ archive."""
        # Create archive
        archive_path = Path(self.test_dir) / "extract_test.tar.gz"
        create_archive(
            archive_path=str(archive_path),
            source_paths=self.test_files[:2],
            use_default_exclusions=False,
            use_gitignore=False
        )
        
        # Extract archive
        extract_dir = Path(self.test_dir) / "targz_extracted"
        result = extract_archive(
            archive_path=str(archive_path),
            extract_dir=str(extract_dir)
        )
        
        self.assertTrue(result['success'])
        self.assertTrue(extract_dir.exists())

    # ========== List Archive Tests ==========
    
    def test_list_zip_archive(self):
        """Test listing contents of ZIP archive."""
        archive_path = Path(self.test_dir) / "list_test.zip"
        create_archive(
            archive_path=str(archive_path),
            source_paths=self.test_files[:3],
            use_default_exclusions=False,
            use_gitignore=False
        )
        
        result = list_archive(archive_path=str(archive_path))
        
        self.assertTrue(result['success'])
        self.assertIsInstance(result['files'], list)
        self.assertGreater(len(result['files']), 0)

    def test_list_tar_archive(self):
        """Test listing contents of TAR archive."""
        archive_path = Path(self.test_dir) / "list_test.tar"
        create_archive(
            archive_path=str(archive_path),
            source_paths=self.test_files[:3],
            use_default_exclusions=False,
            use_gitignore=False
        )
        
        result = list_archive(archive_path=str(archive_path))
        
        self.assertTrue(result['success'])
        self.assertIsInstance(result['files'], list)
        self.assertGreater(len(result['files']), 0)

    def test_list_tar_gz_archive(self):
        """Test listing contents of TAR.GZ archive."""
        archive_path = Path(self.test_dir) / "list_test.tar.gz"
        create_archive(
            archive_path=str(archive_path),
            source_paths=self.test_files[:3],
            use_default_exclusions=False,
            use_gitignore=False
        )
        
        result = list_archive(archive_path=str(archive_path))
        
        self.assertTrue(result['success'])
        self.assertIsInstance(result['files'], list)

    # ========== Error Handling Tests ==========
    
    def test_create_archive_nonexistent_source(self):
        """Test creating archive with nonexistent source."""
        archive_path = Path(self.test_dir) / "error.zip"
        
        result = create_archive(
            archive_path=str(archive_path),
            source_paths=["/nonexistent/path/file.txt"],
            use_default_exclusions=False,
            use_gitignore=False
        )
        
        # Should handle gracefully (might succeed with 0 files or fail)
        self.assertIn('success', result)

    def test_extract_archive_nonexistent_file(self):
        """Test extracting nonexistent archive."""
        extract_dir = Path(self.test_dir) / "extracted"
        
        result = extract_archive(
            archive_path="/nonexistent/archive.zip",
            extract_dir=str(extract_dir)
        )
        
        self.assertFalse(result['success'])
        self.assertIn('message', result)

    def test_list_archive_nonexistent_file(self):
        """Test listing nonexistent archive."""
        result = list_archive(archive_path="/nonexistent/archive.zip")
        
        self.assertFalse(result['success'])
        self.assertIn('message', result)

    # ========== Integration Tests ==========
    
    def test_create_extract_roundtrip_zip(self):
        """Test creating and extracting ZIP archive (roundtrip)."""
        # Create archive
        archive_path = Path(self.test_dir) / "roundtrip.zip"
        create_result = create_archive(
            archive_path=str(archive_path),
            source_paths=self.test_files[:3],
            use_default_exclusions=False,
            use_gitignore=False
        )
        self.assertTrue(create_result['success'])
        
        # Extract archive
        extract_dir = Path(self.test_dir) / "roundtrip_extracted"
        extract_result = extract_archive(
            archive_path=str(archive_path),
            extract_dir=str(extract_dir)
        )
        self.assertTrue(extract_result['success'])
        
        # Verify extracted files exist
        self.assertTrue(extract_dir.exists())
        self.assertGreater(len(list(extract_dir.rglob("*"))), 0)

    def test_create_extract_roundtrip_tar_gz(self):
        """Test creating and extracting TAR.GZ archive (roundtrip)."""
        # Create archive
        archive_path = Path(self.test_dir) / "roundtrip.tar.gz"
        create_result = create_archive(
            archive_path=str(archive_path),
            source_paths=self.test_files[:3],
            use_default_exclusions=False,
            use_gitignore=False
        )
        self.assertTrue(create_result['success'])
        
        # Extract archive
        extract_dir = Path(self.test_dir) / "roundtrip_targz_extracted"
        extract_result = extract_archive(
            archive_path=str(archive_path),
            extract_dir=str(extract_dir)
        )
        self.assertTrue(extract_result['success'])


if __name__ == "__main__":
    unittest.main()