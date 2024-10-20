import unittest
from unittest.mock import patch, MagicMock, call
import os
from io import StringIO
from davai.base_cli import BaseCLI
from davai.git import Git
from davai.requests import CodeUpdateRequest, CodeQueryRequest
from davai.responses import CodeResponse, BaseResponse

class BaseCliTest(unittest.TestCase):
    def setUp(self):
        """Set up the CLI and test environment."""
        # Mock the transport function to return a static response
        self.mock_transport_func = MagicMock(return_value="Mock response")
        self.cli = BaseCLI("TestCLI", self.mock_transport_func, "tmp/src")

        # Mock Git instance methods to prevent actual file operations
        self.cli.git = MagicMock(spec=Git)

        # Create a temporary directory for history files if needed
        self.test_output_dir = "tmp/test_cli"
        if not os.path.exists(self.test_output_dir):
            os.makedirs(self.test_output_dir)
        self.cli.HISTORY_FILE = os.path.join(self.test_output_dir, "cli_history.txt")

    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary files and directories created during testing
        if os.path.exists(self.test_output_dir):
            for file in os.listdir(self.test_output_dir):
                os.remove(os.path.join(self.test_output_dir, file))
            os.rmdir(self.test_output_dir)

    @patch('builtins.input', return_value='y')
    def _test_do_task(self, mock_input):
        """Test the do_task method with a mocked user input."""
        self.cli.git.assets.match.return_value = MagicMock(paths=["src/test.js"])

        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.cli.do_task("Sample task")

            # Verify the mock transport function was called
            self.mock_transport_func.assert_called_once()
            self.assertIn("Mock response", fake_out.getvalue())

    def _test_do_query(self):
        """Test the do_query method with a mocked response."""
        self.cli.git.assets.match.return_value = MagicMock(paths=["src/test_query.js"])

        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.cli.do_query("Sample query")

            # Verify the mock transport function was called
            self.mock_transport_func.assert_called_once()
            self.assertIn("Mock response", fake_out.getvalue())

    @patch('gnureadline.read_history_file')
    @patch('gnureadline.write_history_file')
    def _test_history_load_and_save(self, mock_write, mock_read):
        """Test loading and saving the command history."""
        # Run preloop to load history
        self.cli.preloop()
        mock_read.assert_called_once_with(self.cli.HISTORY_FILE)

        # Run postloop to save history
        self.cli.postloop()
        mock_write.assert_called_once_with(self.cli.HISTORY_FILE)

    @patch('builtins.input', side_effect=['y', 'n'])
    def _test_git_reset_task(self, mock_input):
        """Test git_reset_task method with 'fetch' action and user confirmation."""
        self.cli.git.assets = [MagicMock(head=MagicMock(path="src/fetch_test.js"))]
        self.cli.asset_paths = {"src/fetch_test.js"}

        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.cli.git_reset_task("fetch")

            # Verify the transport function was called
            self.mock_transport_func.assert_called_once()
            self.assertIn("fetch request completed.", fake_out.getvalue())

    def test_do_clear(self):
        """Test the do_clear method."""
        # Add some paths to the asset paths set
        self.cli.asset_paths.add("src/test.js")
        self.cli.asset_paths.add("src/another_test.js")

        # Call the do_clear method
        self.cli.do_clear(None)

        # Check if asset paths have been cleared
        self.assertEqual(len(self.cli.asset_paths), 0)

    @patch('builtins.input', return_value='y')
    def test_diff_display_and_integration(self, mock_input):
        """Test displaying diffs and integrating user-approved changes."""
        old_code = "function test() {\n    console.log('Old');\n}"
        new_code = "function test() {\n    console.log('New');\n}"
        self.cli.git.assets = [MagicMock(head=MagicMock(path="src/test_diff.js"), body=MagicMock(code=old_code))]
        new_asset = MagicMock(head=MagicMock(path="src/test_diff.js"), body=MagicMock(code=new_code))
        self.cli.asset_paths = {"src/test_diff.js"}

        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.cli.print_diff(old_code, new_code)
            output = fake_out.getvalue()

            self.assertIn("console.log('Old');", output)
            self.assertIn("console.log('New');", output)

    def _test_invalid_git_action(self):
        """Test handling of invalid git actions."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            self.cli.git_reset_task("invalid_action")
            self.assertIn("Invalid action", fake_out.getvalue())

if __name__ == '__main__':
    unittest.main()
