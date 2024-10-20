import unittest
from davai.code_block import Head, Body, CodeBlock

class CodeBlockTest(unittest.TestCase):

    def test_head_from_comment_js(self):
        comment = "// src/example.js"
        head = Head.from_comment(comment)
        self.assertIsNotNone(head)
        self.assertEqual(head.path, "src/example.js")
        self.assertEqual(head.code_type, "javascript")

    def test_head_from_comment_css(self):
        comment = "/* src/styles.css */"
        head = Head.from_comment(comment)
        self.assertIsNotNone(head)
        self.assertEqual(head.path, "src/styles.css")
        self.assertEqual(head.code_type, "css")

    def test_head_from_comment_invalid(self):
        comment = "# some other comment"
        head = Head.from_comment(comment)
        self.assertIsNone(head)

    def test_head_as_comment_js(self):
        head = Head("src/example.js")
        self.assertEqual(head.as_comment(), "// src/example.js\n")

    def test_head_as_comment_css(self):
        head = Head("src/styles.css")
        self.assertEqual(head.as_comment(), "/* src/styles.css */\n")

    def _test_body_extraction_ignores_initial_blank_lines_and_comments(self):
        code = """
        // Some initial comment
        // Another comment
        
        line_of_code_1();
        line_of_code_2();
        """
        body = Body(code)
        expected_body = "line_of_code_1();\nline_of_code_2();"
        self.assertEqual(body.code.strip(), expected_body)

    def _test_body_extraction_retains_mid_and_trailing_blank_lines(self):
        code = """
        line_of_code_1();
        
        line_of_code_2();
        
        """
        body = Body(code)
        expected_body = "line_of_code_1();\n\nline_of_code_2();\n"
        self.assertEqual(body.code, expected_body)

    def test_body_without_comments(self):
        code = """
        line_of_code_1();
        line_of_code_2();
        """
        body = Body(code)
        expected_body = "line_of_code_1();\nline_of_code_2();"
        self.assertEqual(body.code.strip(), expected_body)

    def test_code_block_parsing_js(self):
        code_block = """
        // src/Example.js
        function example() {
            console.log("Hello World");
        }
        """
        code_block_obj = CodeBlock.parse(code_block)
        self.assertIsNotNone(code_block_obj)
        self.assertEqual(code_block_obj.head.path, "src/Example.js")
        self.assertEqual(code_block_obj.body.code.strip(), 'function example() {\n    console.log("Hello World");\n}')

    def test_code_block_parsing_css(self):
        code_block = """
        /* src/styles.css */
        body {
            background-color: black;
        }
        """
        code_block_obj = CodeBlock.parse(code_block)
        self.assertIsNotNone(code_block_obj)
        self.assertEqual(code_block_obj.head.path, "src/styles.css")
        self.assertEqual(code_block_obj.body.code.strip(), "body {\n    background-color: black;\n}")

    def _test_code_block_representation(self):
        head = Head("src/Example.js")
        body = Body("""
        function example() {
            console.log("Hello World");
        }
        """)
        code_block = CodeBlock(head, body)
        repr_string = repr(code_block).strip()
        expected_repr = """
        ```javascript
        // src/Example.js
        function example() {
            console.log("Hello World");
        }
        ```
        """.strip()
        self.assertEqual(repr_string, expected_repr)
        
if __name__ == "__main__":
    unittest.main()
