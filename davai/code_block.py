import re

class Head:
    """
    Class representing the head (path) of a code block.
    This class manages the parsing and rendering of a file path as a comment.
    """
    def __init__(self, path):
        self.path = path

    @staticmethod
    def from_comment(comment):
        """
        Initialize a Head object from a comment containing a path.
        Extracts the asset path from the comment based on the expected comment format.
        Supports JS, CSS, Dart, and TypeScript files.
        """
        # Check for JS comment style: // src/Hello.js or // src/Hello.ts
        js_ts_pattern = r"^//\s*(src/[\w\d/_-]+\.(js|ts|dart))"
        # Check for CSS comment style: /* src/styles.css */
        css_pattern = r"^/\*\s*(src/[\w\d/_-]+\.css)\s*\*/"

        # Match the comment pattern for JS, TS, Dart, or CSS
        js_ts_match = re.match(js_ts_pattern, comment.strip())
        css_match = re.match(css_pattern, comment.strip())

        if js_ts_match:
            return Head(js_ts_match.group(1))  # Return Head with JS/TS/Dart path
        elif css_match:
            return Head(css_match.group(1))  # Return Head with CSS path
        else:
            return None  # No valid asset path found

    @property
    def code_type(self):
        """
        Returns the Markdown-compatible code type based on the file extension.
        Supports JavaScript, TypeScript, Dart, and CSS.
        """
        if self.path.endswith(".js"):
            return "javascript"
        elif self.path.endswith(".ts"):
            return "typescript"
        elif self.path.endswith(".dart"):
            return "dart"
        elif self.path.endswith(".css"):
            return "css"
        else:
            return ""  # Fallback for unknown types
        
    def as_comment(self):
        """
        Renders the path as a comment based on the file type (JS, TS, Dart, or CSS).
        """
        if self.path.endswith(".js") or self.path.endswith(".ts") or self.path.endswith(".dart"):
            return f"// {self.path}\n"
        elif self.path.endswith(".css"):
            return f"/* {self.path} */\n"
        else:
            return f"# {self.path}\n"  # Fallback for other file types


class Body:
    """
    Class representing the body (code content) of a code block.
    """
    def __init__(self, code):
        self.code = self._extract_body(code)

    def _extract_body(self, code):
        """
        Extracts the body content, ignoring initial blank lines and comment lines.
        Stops ignoring once the first non-blank/non-comment line is encountered.
        """
        lines = code.split("\n")
        body_lines = []
        start_processing = False

        for line in lines:
            stripped_line = line.strip()

            # Start adding lines once we encounter a non-blank/non-comment line
            if not start_processing and stripped_line and not Head.from_comment(stripped_line):
                start_processing = True
            
            # Add the line if we've started processing
            if start_processing:
                body_lines.append(line)

        return "\n".join(body_lines)

    def __repr__(self):
        """
        Renders the body (code content).
        """
        return self.code


class CodeBlock:
    """
    Class representing a code block with head (path) and body (code content).
    """
    def __init__(self, head, body):
        self.head = head  # Expecting a Head object
        self.body = body  # Expecting a Body object

    def __repr__(self):
        """
        Renders the code block with the head as a comment in the first line and body as the code.
        The output is enclosed in Markdown-style backticks with the appropriate code type.
        """
        return f"```{self.head.code_type}\n{self.head.as_comment()}{repr(self.body)}\n```"

    @staticmethod
    def parse(code_block):
        """
        Parse a code_block string into Head (path) and Body (code content) objects by extracting
        the asset name from the comment.
        Returns an instance of CodeBlock.
        """
        # Split the code block into lines
        code_block_lines = code_block.split("\n")

        # Find the first non-blank line to use as the comment
        first_line = next((line.strip() for line in code_block_lines if line.strip()), None)

        if not first_line:
            return None  # Return None if no non-blank line (comment) is found

        head = Head.from_comment(first_line)

        if head:
            # Pass the entire code block content to the Body constructor
            body = Body("\n".join(code_block_lines))
            return CodeBlock(head, body)
        return None
