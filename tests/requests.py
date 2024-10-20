import unittest
import os
from datetime import datetime
from davai.requests import BaseRequest, CodeUpdateRequest, CodeQueryRequest, CodeResetRequest
from davai.code_block import CodeBlock, Head, Body

class RequestsTest(unittest.TestCase):
    def setUp(self):
        """Set up test environment and assets."""
        # Create a temporary directory for saving requests
        self.test_output_dir = "tmp/test_requests"
        if not os.path.exists(self.test_output_dir):
            os.makedirs(self.test_output_dir)

        # Create dummy CodeBlocks
        self.code_block_1 = CodeBlock(Head("src/App.js"), Body("console.log('Hello World');"))
        self.code_block_2 = CodeBlock(Head("src/styles.css"), Body("body { background-color: black; }"))
        self.assets = [self.code_block_1, self.code_block_2]

    def tearDown(self):
        """Clean up the test environment."""
        # Remove all files created during tests
        for file in os.listdir(self.test_output_dir):
            os.remove(os.path.join(self.test_output_dir, file))
        os.rmdir(self.test_output_dir)

    def test_base_request_generate(self):
        """Test that BaseRequest generates the request text correctly."""
        request = BaseRequest()
        content = "Test content"
        request.generate(content)
        self.assertEqual(request.request_text, content)

    def test_base_request_save(self):
        """Test that BaseRequest saves the request text to a file."""
        request = BaseRequest()
        content = "Test content for saving"
        request.generate(content)
        request.save(self.test_output_dir)

        # Check if the file was created
        saved_files = os.listdir(self.test_output_dir)
        self.assertEqual(len(saved_files), 1)
        self.assertTrue(saved_files[0].startswith("request_"))

        # Check file content
        with open(os.path.join(self.test_output_dir, saved_files[0]), 'r') as file:
            file_content = file.read()
            self.assertEqual(file_content, content)

    def test_code_update_request_generate(self):
        """Test that CodeUpdateRequest generates the request text correctly with assets."""
        request = CodeUpdateRequest()
        prompt_text = "Update the code to improve performance."
        request.generate(prompt_text, self.assets)

        # Assert that the generated request includes both assets and the prompt text
        self.assertIn("Please analyze the following code blocks", request.request_text)
        self.assertIn("console.log('Hello World');", request.request_text)
        self.assertIn("body { background-color: black; }", request.request_text)
        self.assertIn("Update the code to improve performance.", request.request_text)

    def test_code_query_request_generate(self):
        """Test that CodeQueryRequest generates the request text correctly with assets."""
        request = CodeQueryRequest()
        prompt_text = "What does this code do?"
        request.generate(prompt_text, self.assets)

        # Assert that the generated request includes both assets and the prompt text
        self.assertIn("Please analyze the following code blocks", request.request_text)
        self.assertIn("What does this code do?", request.request_text)
        self.assertIn("console.log('Hello World');", request.request_text)
        self.assertIn("body { background-color: black; }", request.request_text)
        self.assertIn("Please provide a textual explanation or analysis only.", request.request_text)

    def test_code_reset_request_generate(self):
        """Test that CodeResetRequest generates the request text correctly with assets."""
        request = CodeResetRequest()
        request.generate(self.assets)

        # Assert that the generated request includes both assets
        self.assertIn("Please use the following code blocks as the latest versions of these files.", request.request_text)
        self.assertIn("console.log('Hello World');", request.request_text)
        self.assertIn("body { background-color: black; }", request.request_text)
        self.assertIn("Please acknowledge that these files will now be considered the latest versions", request.request_text)

    def test_code_update_request_save(self):
        """Test that CodeUpdateRequest saves the request text to a file."""
        request = CodeUpdateRequest()
        prompt_text = "Update the code to fix the bug."
        request.generate(prompt_text, self.assets)
        request.save(self.test_output_dir)

        # Check if the file was created
        saved_files = os.listdir(self.test_output_dir)
        self.assertEqual(len(saved_files), 1)
        self.assertTrue(saved_files[0].startswith("request_"))

        # Check file content
        with open(os.path.join(self.test_output_dir, saved_files[0]), 'r') as file:
            file_content = file.read()
            self.assertIn("Update the code to fix the bug.", file_content)

if __name__ == '__main__':
    unittest.main()
