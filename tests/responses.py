import unittest
import os
import re
from datetime import datetime
from davai.responses import BaseResponse, CodeResponse
from davai.code_block import CodeBlock, Head, Body

class ResponsesTest(unittest.TestCase):
    def setUp(self):
        """Set up the test environment and response text."""
        self.test_output_dir = "tmp/test_responses"
        if not os.path.exists(self.test_output_dir):
            os.makedirs(self.test_output_dir)

        # Sample response text containing code blocks
        self.sample_response_text = (
            "Here are the updated code blocks:\n\n"
            "```javascript\n// src/App.js\nfunction example() {\n    console.log('Hello World');\n}\n```\n"
            "```css\n/* src/styles.css */\nbody {\n    background-color: black;\n}\n```"
        )
        self.sample_response_text_without_code_blocks = (
            "Here is some text without code blocks. It contains explanations but no code."
        )

    def tearDown(self):
        """Clean up the test environment."""
        for file in os.listdir(self.test_output_dir):
            os.remove(os.path.join(self.test_output_dir, file))
        os.rmdir(self.test_output_dir)

    def test_base_response_save(self):
        """Test that BaseResponse saves the response text to a file."""
        response = BaseResponse("This is a sample response text.")
        response.save(self.test_output_dir)

        # Check if the file was created
        saved_files = os.listdir(self.test_output_dir)
        self.assertEqual(len(saved_files), 1)
        self.assertTrue(saved_files[0].startswith("response_"))

        # Check file content
        with open(os.path.join(self.test_output_dir, saved_files[0]), 'r') as file:
            file_content = file.read()
            self.assertEqual(file_content, "This is a sample response text.")

    def test_code_response_extract_code_blocks(self):
        """Test that CodeResponse correctly extracts code blocks."""
        response = CodeResponse(self.sample_response_text)
        assets = response.extract_code_blocks()

        # Check that two code blocks were extracted
        self.assertEqual(len(assets), 2)

        # Check that the paths and content are correctly extracted
        self.assertEqual(assets[0].head.path, "src/App.js")
        self.assertEqual(assets[0].body.code.strip(), "function example() {\n    console.log('Hello World');\n}")

        self.assertEqual(assets[1].head.path, "src/styles.css")
        self.assertEqual(assets[1].body.code.strip(), "body {\n    background-color: black;\n}")

    def test_code_response_extract_code_blocks_no_blocks(self):
        """Test that CodeResponse returns an empty assets list when no code blocks are present."""
        response = CodeResponse(self.sample_response_text_without_code_blocks)
        assets = response.extract_code_blocks()

        # Assert that no code blocks are extracted
        self.assertEqual(len(assets), 0)

    def test_code_response_extract_code_blocks_invalid_blocks(self):
        """Test that CodeResponse handles cases where code blocks do not have valid comments."""
        invalid_response_text = (
            "Here are some blocks:\n\n"
            "```javascript\nfunction example() {\n    console.log('Hello World');\n}\n```\n"
            "```css\nbody {\n    background-color: black;\n}\n```"
        )
        response = CodeResponse(invalid_response_text)
        assets = response.extract_code_blocks()

        # Assert that no code blocks are extracted because comments are missing
        self.assertEqual(len(assets), 0)

    def test_code_response_partial_extraction(self):
        """Test that CodeResponse extracts code blocks where only some blocks have valid comments."""
        partial_response_text = (
            "Here are some blocks:\n\n"
            "```javascript\n// src/App.js\nfunction example() {\n    console.log('Hello World');\n}\n```\n"
            "```css\nbody {\n    background-color: black;\n}\n```"
        )
        response = CodeResponse(partial_response_text)
        assets = response.extract_code_blocks()

        # Assert that only one valid code block is extracted
        self.assertEqual(len(assets), 1)
        self.assertEqual(assets[0].head.path, "src/App.js")
        self.assertEqual(assets[0].body.code.strip(), "function example() {\n    console.log('Hello World');\n}")

if __name__ == '__main__':
    unittest.main()
