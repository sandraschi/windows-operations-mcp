import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.windows_operations_mcp.tools.powershell_tools import (
    register_powershell_tools
)


class MockMCP:
    """Mock MCP server for testing."""
    def __init__(self):
        self.tools = {}

    def tool(self, func=None, **kwargs):
        if func is None:
            def decorator(f):
                self.tools[f.__name__] = f
                return f
            return decorator
        else:
            self.tools[func.__name__] = func
            return func


class TestPowerShellTools(unittest.TestCase):
    """Test PowerShell tools functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.mcp = MockMCP()
        register_powershell_tools(self.mcp)

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # ========== Tool Registration Tests ==========
    
    def test_register_powershell_tools(self):
        """Test PowerShell tools registration."""
        self.assertIn('run_powershell', self.mcp.tools)
        self.assertIn('run_cmd', self.mcp.tools)

    # ========== PowerShell Execution Tests ==========
    
    def test_run_powershell_simple_command(self):
        """Test running simple PowerShell command."""
        run_powershell = self.mcp.tools['run_powershell']
        
        result = run_powershell(command="Write-Output 'Hello PowerShell'")
        
        self.assertTrue(result['success'])
        self.assertIn('Hello PowerShell', result['stdout'])
        self.assertEqual(result['exit_code'], 0)

    def test_run_powershell_get_process(self):
        """Test running PowerShell Get-Process command."""
        run_powershell = self.mcp.tools['run_powershell']
        
        result = run_powershell(
            command="Get-Process | Select-Object -First 1 | Select-Object ProcessName"
        )
        
        self.assertTrue(result['success'])
        self.assertIn('ProcessName', result['stdout'])

    def test_run_powershell_with_variables(self):
        """Test running PowerShell with variables."""
        run_powershell = self.mcp.tools['run_powershell']
        
        result = run_powershell(
            command="$testVar = 'Hello'; Write-Output $testVar"
        )
        
        self.assertTrue(result['success'])
        self.assertIn('Hello', result['stdout'])

    def test_run_powershell_multiline_command(self):
        """Test running multiline PowerShell command."""
        run_powershell = self.mcp.tools['run_powershell']
        
        command = """
        $sum = 0
        1..5 | ForEach-Object { $sum += $_ }
        Write-Output $sum
        """
        
        result = run_powershell(command=command)
        
        self.assertTrue(result['success'])
        self.assertIn('15', result['stdout'])

    def test_run_powershell_with_working_directory(self):
        """Test running PowerShell in specific directory."""
        run_powershell = self.mcp.tools['run_powershell']
        
        result = run_powershell(
            command="Get-Location | Select-Object -ExpandProperty Path",
            working_directory=self.test_dir
        )
        
        self.assertTrue(result['success'])
        # Working directory should be in the output
        self.assertIn(os.path.basename(self.test_dir), result['stdout'] or "")

    def test_run_powershell_with_timeout(self):
        """Test PowerShell command with timeout."""
        run_powershell = self.mcp.tools['run_powershell']
        
        # Quick command should complete
        result = run_powershell(
            command="Write-Output 'Fast'",
            timeout_seconds=5
        )
        
        self.assertTrue(result['success'])

    def test_run_powershell_error_handling(self):
        """Test PowerShell error handling."""
        run_powershell = self.mcp.tools['run_powershell']
        
        # Command that will fail
        result = run_powershell(
            command="Get-NonexistentCmdlet"
        )
        
        self.assertFalse(result['success'])
        self.assertNotEqual(result['exit_code'], 0)

    def test_run_powershell_with_special_characters(self):
        """Test PowerShell with special characters."""
        run_powershell = self.mcp.tools['run_powershell']
        
        result = run_powershell(
            command="Write-Output 'Special chars: @#$%^&*()'"
        )
        
        self.assertTrue(result['success'])
        self.assertIn('Special chars', result['stdout'])

    def test_run_powershell_json_output(self):
        """Test PowerShell command with JSON output."""
        run_powershell = self.mcp.tools['run_powershell']
        
        result = run_powershell(
            command="@{Name='Test'; Value=42} | ConvertTo-Json"
        )
        
        self.assertTrue(result['success'])
        self.assertIn('Name', result['stdout'])
        self.assertIn('Test', result['stdout'])

    # ========== CMD Execution Tests ==========
    
    def test_run_cmd_simple_command(self):
        """Test running simple CMD command."""
        run_cmd = self.mcp.tools['run_cmd']
        
        result = run_cmd(command="echo Hello CMD")
        
        self.assertTrue(result['success'])
        self.assertIn('Hello CMD', result['stdout'])
        self.assertEqual(result['exit_code'], 0)

    def test_run_cmd_dir_command(self):
        """Test running CMD dir command."""
        run_cmd = self.mcp.tools['run_cmd']
        
        result = run_cmd(
            command="dir /b",
            working_directory=self.test_dir
        )
        
        self.assertTrue(result['success'])

    def test_run_cmd_with_working_directory(self):
        """Test running CMD in specific directory."""
        run_cmd = self.mcp.tools['run_cmd']
        
        # Create a test file
        test_file = Path(self.test_dir) / "test.txt"
        test_file.write_text("test content")
        
        result = run_cmd(
            command="dir /b test.txt",
            working_directory=self.test_dir
        )
        
        self.assertTrue(result['success'])
        self.assertIn('test.txt', result['stdout'])

    def test_run_cmd_with_environment_variable(self):
        """Test CMD with environment variable."""
        run_cmd = self.mcp.tools['run_cmd']
        
        result = run_cmd(command="echo %PATH%")
        
        self.assertTrue(result['success'])
        # PATH should be in output
        self.assertGreater(len(result['stdout']), 0)

    def test_run_cmd_multiple_commands(self):
        """Test running multiple CMD commands."""
        run_cmd = self.mcp.tools['run_cmd']
        
        result = run_cmd(
            command="echo First && echo Second"
        )
        
        self.assertTrue(result['success'])
        self.assertIn('First', result['stdout'])
        self.assertIn('Second', result['stdout'])

    def test_run_cmd_error_handling(self):
        """Test CMD error handling."""
        run_cmd = self.mcp.tools['run_cmd']
        
        # Command that will fail
        result = run_cmd(command="nonexistent_command_xyz")
        
        self.assertFalse(result['success'])
        self.assertNotEqual(result['exit_code'], 0)
        self.assertIn('not recognized', result['stderr'].lower())

    def test_run_cmd_with_timeout(self):
        """Test CMD command with timeout."""
        run_cmd = self.mcp.tools['run_cmd']
        
        # Quick command should complete
        result = run_cmd(
            command="echo Quick",
            timeout_seconds=5
        )
        
        self.assertTrue(result['success'])

    # ========== Integration Tests ==========
    
    def test_powershell_cmd_comparison(self):
        """Test that PowerShell and CMD can run equivalent commands."""
        run_powershell = self.mcp.tools['run_powershell']
        run_cmd = self.mcp.tools['run_cmd']
        
        # Create test file
        test_file = Path(self.test_dir) / "test.txt"
        test_file.write_text("test content")
        
        # PowerShell version
        ps_result = run_powershell(
            command=f"Test-Path '{test_file}'",
            working_directory=self.test_dir
        )
        
        # CMD version
        cmd_result = run_cmd(
            command=f"if exist {test_file.name} echo EXISTS",
            working_directory=self.test_dir
        )
        
        self.assertTrue(ps_result['success'])
        self.assertTrue(cmd_result['success'])

    def test_powershell_file_operations(self):
        """Test PowerShell file operations."""
        run_powershell = self.mcp.tools['run_powershell']
        
        test_file = Path(self.test_dir) / "ps_test.txt"
        
        # Create file
        result = run_powershell(
            command=f"Set-Content -Path '{test_file}' -Value 'PowerShell created this'"
        )
        self.assertTrue(result['success'])
        
        # Verify file exists
        self.assertTrue(test_file.exists())
        self.assertIn('PowerShell created this', test_file.read_text())

    def test_cmd_file_operations(self):
        """Test CMD file operations."""
        run_cmd = self.mcp.tools['run_cmd']
        
        test_file = Path(self.test_dir) / "cmd_test.txt"
        
        # Create file
        result = run_cmd(
            command=f"echo CMD created this > {test_file.name}",
            working_directory=self.test_dir
        )
        self.assertTrue(result['success'])
        
        # Verify file exists
        self.assertTrue(test_file.exists())

    def test_powershell_complex_pipeline(self):
        """Test complex PowerShell pipeline."""
        run_powershell = self.mcp.tools['run_powershell']
        
        command = """
        1..10 | 
        Where-Object { $_ % 2 -eq 0 } | 
        ForEach-Object { $_ * 2 } | 
        Measure-Object -Sum | 
        Select-Object -ExpandProperty Sum
        """
        
        result = run_powershell(command=command)
        
        self.assertTrue(result['success'])
        # Sum of even numbers 1-10, doubled: (2+4+6+8+10)*2 = 60
        self.assertIn('60', result['stdout'])

    # ========== Security and Safety Tests ==========
    
    def test_powershell_script_block_safety(self):
        """Test PowerShell script block execution safety."""
        run_powershell = self.mcp.tools['run_powershell']
        
        # Test that script blocks work
        result = run_powershell(
            command="& { Write-Output 'Safe script block' }"
        )
        
        self.assertTrue(result['success'])
        self.assertIn('Safe script block', result['stdout'])

    def test_cmd_path_validation(self):
        """Test CMD path validation."""
        run_cmd = self.mcp.tools['run_cmd']
        
        # Test with valid path
        result = run_cmd(
            command="echo test",
            working_directory=self.test_dir
        )
        
        self.assertTrue(result['success'])

    # ========== Output Handling Tests ==========
    
    def test_powershell_large_output(self):
        """Test PowerShell with large output."""
        run_powershell = self.mcp.tools['run_powershell']
        
        # Generate 100 lines of output
        command = "1..100 | ForEach-Object { Write-Output \"Line $_\" }"
        
        result = run_powershell(command=command)
        
        self.assertTrue(result['success'])
        self.assertGreater(len(result['stdout']), 0)

    def test_cmd_large_output(self):
        """Test CMD with large output."""
        run_cmd = self.mcp.tools['run_cmd']
        
        # Create multiple echo statements
        command = " && ".join([f"echo Line {i}" for i in range(1, 11)])
        
        result = run_cmd(command=command)
        
        self.assertTrue(result['success'])
        self.assertGreater(len(result['stdout']), 0)

    def test_powershell_unicode_output(self):
        """Test PowerShell with unicode output."""
        run_powershell = self.mcp.tools['run_powershell']
        
        result = run_powershell(
            command="Write-Output '🚀 Unicode test: αβγδ 中文'"
        )
        
        # Should handle unicode gracefully
        self.assertTrue(result['success'])


if __name__ == "__main__":
    unittest.main()