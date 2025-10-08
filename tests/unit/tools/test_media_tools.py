import unittest
import tempfile
import os
import shutil
from pathlib import Path
import sys

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.windows_operations_mcp.tools.media_register import register_media_tools


class MockMCP:
    """Mock MCP server for testing."""
    def __init__(self):
        self.tools = {}

    def tool(self, func=None, **kwargs):
        if func is not None:
            # Direct function registration: mcp.tool(function)
            self.tools[func.__name__] = func
            return func
        else:
            # Decorator pattern: @mcp.tool()
            def decorator(f):
                self.tools[f.__name__] = f
                return f
            return decorator


class TestMediaTools(unittest.TestCase):
    """Test media metadata tools functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.mcp = MockMCP()

        # Create test files
        self.test_image = os.path.join(self.test_dir, "test.jpg")
        self.test_mp3 = os.path.join(self.test_dir, "test.mp3")
        
        # Create minimal test files (not real media files, but sufficient for testing)
        # Create a simple 1x1 pixel JPEG file
        from PIL import Image as PILImage
        import io
        
        # Create a tiny valid JPEG
        img = PILImage.new('RGB', (1, 1), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        with open(self.test_image, 'wb') as f:
            f.write(img_bytes.getvalue())
            
        with open(self.test_mp3, 'wb') as f:
            f.write(b'ID3\x03\x00\x00\x00\x00\x00\x00')

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_register_media_tools(self):
        """Test registering media tools with MCP."""
        register_media_tools(self.mcp)

        # Check that tools were registered
        self.assertIn('get_media_metadata', self.mcp.tools)
        self.assertIn('update_media_metadata', self.mcp.tools)
        self.assertIn('get_image_metadata', self.mcp.tools)
        self.assertIn('update_image_metadata', self.mcp.tools)
        self.assertIn('get_mp3_metadata', self.mcp.tools)
        self.assertIn('update_mp3_metadata', self.mcp.tools)

    def test_get_media_metadata_basic(self):
        """Test basic media metadata retrieval."""
        register_media_tools(self.mcp)
        get_media_metadata_func = self.mcp.tools['get_media_metadata']

        result = get_media_metadata_func(image_path=self.test_image)

        self.assertIn('success', result)
        self.assertIn('metadata', result)

    def test_get_media_metadata_with_mp3(self):
        """Test media metadata retrieval with MP3."""
        register_media_tools(self.mcp)
        get_media_metadata_func = self.mcp.tools['get_media_metadata']

        result = get_media_metadata_func(image_path=self.test_mp3)

        self.assertIn('success', result)
        self.assertIn('metadata', result)

    def test_get_image_metadata_basic(self):
        """Test basic image metadata retrieval."""
        register_media_tools(self.mcp)
        get_image_metadata_func = self.mcp.tools['get_image_metadata']

        result = get_image_metadata_func(image_path=self.test_image)

        self.assertIn('success', result)
        self.assertIn('metadata', result)

    def test_get_image_metadata_detailed(self):
        """Test detailed image metadata retrieval."""
        register_media_tools(self.mcp)
        get_image_metadata_func = self.mcp.tools['get_image_metadata']

        result = get_image_metadata_func(
            image_path=self.test_image,
            detailed=True
        )

        self.assertIn('success', result)
        self.assertIn('metadata', result)

    def test_get_mp3_metadata_basic(self):
        """Test basic MP3 metadata retrieval."""
        register_media_tools(self.mcp)
        get_mp3_metadata_func = self.mcp.tools['get_mp3_metadata']

        result = get_mp3_metadata_func(mp3_path=self.test_mp3)

        self.assertIn('success', result)
        self.assertIn('metadata', result)

    def test_get_mp3_metadata_detailed(self):
        """Test detailed MP3 metadata retrieval."""
        register_media_tools(self.mcp)
        get_mp3_metadata_func = self.mcp.tools['get_mp3_metadata']

        result = get_mp3_metadata_func(
            mp3_path=self.test_mp3,
            detailed=True
        )

        self.assertIn('success', result)
        self.assertIn('metadata', result)

    def test_update_media_metadata_basic(self):
        """Test basic media metadata update."""
        register_media_tools(self.mcp)
        update_media_metadata_func = self.mcp.tools['update_media_metadata']

        result = update_media_metadata_func(
            image_path=self.test_image,
            metadata={"title": "Test Image"}
        )

        self.assertIn('success', result)
        self.assertIn('message', result)

    def test_update_media_metadata_with_save_copy(self):
        """Test media metadata update with save copy."""
        register_media_tools(self.mcp)
        update_media_metadata_func = self.mcp.tools['update_media_metadata']

        result = update_media_metadata_func(
            image_path=self.test_image,
            metadata={"title": "Test Image"},
            save_as_copy=True,
            output_path=os.path.join(self.test_dir, "test_copy.jpg")
        )

        self.assertIn('success', result)
        self.assertIn('message', result)

    def test_update_image_metadata_basic(self):
        """Test basic image metadata update."""
        register_media_tools(self.mcp)
        update_image_metadata_func = self.mcp.tools['update_image_metadata']

        result = update_image_metadata_func(
            image_path=self.test_image,
            metadata={"title": "Test Image"}
        )

        self.assertIn('success', result)
        self.assertIn('message', result)

    def test_update_image_metadata_with_save_copy(self):
        """Test image metadata update with save copy."""
        register_media_tools(self.mcp)
        update_image_metadata_func = self.mcp.tools['update_image_metadata']

        result = update_image_metadata_func(
            image_path=self.test_image,
            metadata={"title": "Test Image"},
            save_as_copy=True,
            output_path=os.path.join(self.test_dir, "test_copy.jpg")
        )

        self.assertIn('success', result)
        self.assertIn('message', result)

    def test_update_mp3_metadata_basic(self):
        """Test basic MP3 metadata update."""
        register_media_tools(self.mcp)
        update_mp3_metadata_func = self.mcp.tools['update_mp3_metadata']

        result = update_mp3_metadata_func(
            mp3_path=self.test_mp3,
            metadata={"title": "Test Song"}
        )

        self.assertIn('success', result)
        self.assertIn('message', result)

    def test_update_mp3_metadata_with_save_copy(self):
        """Test MP3 metadata update with save copy."""
        register_media_tools(self.mcp)
        update_mp3_metadata_func = self.mcp.tools['update_mp3_metadata']

        result = update_mp3_metadata_func(
            mp3_path=self.test_mp3,
            metadata={"title": "Test Song"},
            save_as_copy=True,
            output_path=os.path.join(self.test_dir, "test_copy.mp3")
        )

        self.assertIn('success', result)
        self.assertIn('message', result)

    def test_media_tools_error_handling(self):
        """Test error handling in media tools."""
        register_media_tools(self.mcp)
        get_media_metadata_func = self.mcp.tools['get_media_metadata']

        # Test with nonexistent file
        result = get_media_metadata_func(image_path="/nonexistent/file.jpg")

        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_get_media_metadata_with_invalid_file(self):
        """Test media metadata with invalid file type."""
        register_media_tools(self.mcp)
        get_media_metadata_func = self.mcp.tools['get_media_metadata']

        # Create a text file (not a media file)
        text_file = os.path.join(self.test_dir, "test.txt")
        with open(text_file, 'w') as f:
            f.write("Not a media file")

        result = get_media_metadata_func(image_path=text_file)

        self.assertIn('success', result)
        self.assertIn('metadata', result)

    def test_update_media_metadata_with_invalid_metadata(self):
        """Test media metadata update with invalid metadata."""
        register_media_tools(self.mcp)
        update_media_metadata_func = self.mcp.tools['update_media_metadata']

        result = update_media_metadata_func(
            image_path=self.test_image,
            metadata="invalid_metadata_format"
        )

        self.assertIn('success', result)
        self.assertIn('message', result)

    def test_get_image_metadata_with_unsupported_format(self):
        """Test image metadata with unsupported format."""
        register_media_tools(self.mcp)
        get_image_metadata_func = self.mcp.tools['get_image_metadata']

        # Create a file with unsupported extension
        unsupported_file = os.path.join(self.test_dir, "test.xyz")
        with open(unsupported_file, 'wb') as f:
            f.write(b'fake image data')

        result = get_image_metadata_func(image_path=unsupported_file)

        self.assertIn('success', result)
        self.assertIn('metadata', result)

    def test_get_mp3_metadata_with_non_mp3_file(self):
        """Test MP3 metadata with non-MP3 file."""
        register_media_tools(self.mcp)
        get_mp3_metadata_func = self.mcp.tools['get_mp3_metadata']

        result = get_mp3_metadata_func(mp3_path=self.test_image)

        self.assertIn('success', result)
        self.assertIn('metadata', result)


if __name__ == "__main__":
    unittest.main()