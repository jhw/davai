import os
import logging
import re
from datetime import datetime
from davai.assets import Assets
from davai.code_block import CodeBlock

class BaseResponse:
    """
    Base class to handle generic API responses.
    """
    def __init__(self, response_text):
        self.response_text = response_text

    def save(self, output_dir="tmp/responses"):
        """
        Save the response text to a file in the specified directory (default: tmp/responses).
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        response_filename = os.path.join(output_dir, f"response_{timestamp}.txt")
        with open(response_filename, 'w') as response_file:
            response_file.write(self.response_text)
        logging.info(f"Response saved to {response_filename}")

class CodeResponse(BaseResponse):
    """
    Class to handle API responses containing code blocks.
    Inherits from BaseResponse and adds functionality to extract and process code blocks.
    """
    def extract_code_blocks(self):
        """
        Extracts code blocks from the response text.
        Returns an instance of Assets (a list of CodeBlock objects).
        """
        assets = Assets()
        code_blocks = re.findall(r"```[a-z]*\n(.*?)\n```", self.response_text, re.DOTALL)

        for i, code_block in enumerate(code_blocks):
            parsed_code_block = CodeBlock.parse(code_block)
            if parsed_code_block:
                assets.append(parsed_code_block)
            else:
                logging.warning(f"Code block {i+1}: No asset name comment found in the first line.")
        
        return assets
