import os
import logging
from datetime import datetime

class BaseRequest:
    """
    Base class to handle generic API requests.
    """
    def __init__(self):
        self.request_text = None  # Holds the generated request text

    def generate(self, content):
        """
        Generates the request based on the provided content.
        This method should be overridden by subclasses to include specific request logic.
        """
        self.request_text = content

    def save(self, output_dir="tmp/requests"):
        """
        Save the generated request to a file in the specified directory (default: tmp/requests).
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        request_filename = os.path.join(output_dir, f"request_{timestamp}.txt")
        with open(request_filename, 'w') as request_file:
            request_file.write(self.request_text)
        logging.info(f"Request saved to {request_filename}")

class CodeUpdateRequest(BaseRequest):
    """
    Class to handle task-specific API requests.
    Inherits from BaseRequest and extends it with task-related generation logic.
    """
    def generate(self, prompt_text, assets):
        """
        Generates the task request based on the provided prompt text and assets.
        """
        buf = []
        
        # Include preamble if assets exist
        if assets:
            buf.append("Please analyze the following code blocks, then I will set a task for you.")
            buf.append("The asset name will be contained as a comment in the first line of each code block.")
            buf.append("It's important to echo these comments in the response code blocks, to aid code reintegration.")

            # Rendering each code block now automatically includes the code type and backticks
            for code_block in assets:
                buf.append(repr(code_block))
            buf.append("---")
        
        # Always include the user request
        buf.append(prompt_text)
        
        # Add the postamble for code integration instructions
        buf.append("You don't need to return any comments; just returning code blocks is fine.")
        buf.append("Please only return modified files; you don't need to echo any unchanged files.")
        
        # Call the parent's generate method to store the generated request text
        super().generate("\n\n".join(buf))

class CodeQueryRequest(BaseRequest):
    """
    Class to handle code query API requests.
    Inherits from BaseRequest and extends it with query-specific generation logic.
    """
    def generate(self, prompt_text, assets):
        """
        Generates the query request based on the provided prompt text and assets.
        """
        buf = []
        
        # Include preamble if assets exist
        if assets:
            buf.append("Please analyze the following code blocks. I will set a task for you.")
            buf.append("The asset name will be contained as a comment in the first line of each code block.")
            buf.append("It's important to review these code blocks before responding to the query.")

            # Rendering each code block now automatically includes the code type and backticks
            for code_block in assets:
                buf.append(repr(code_block))
            buf.append("---")
        
        # Always include the user request
        buf.append(prompt_text)
        
        # Add the postamble instructing to reply in text only
        buf.append("Please provide a textual explanation or analysis only. Do not return any code blocks or code snippets.")
        
        # Call the parent's generate method to store the generated request text
        super().generate("\n\n".join(buf))
        
class CodeResetRequest(BaseRequest):
    """
    Class to handle code reset API requests.
    Inherits from BaseRequest and extends it with reset-specific generation logic.
    """
    def generate(self, assets):
        """
        Generates the reset request based on the provided assets.
        """
        buf = []
        
        # Include preamble indicating that these code blocks should be used as the latest versions
        if assets:
            buf.append("Please use the following code blocks as the latest versions of these files.")
            buf.append("The asset name will be contained as a comment in the first line of each code block.")
            buf.append("There is no need for further response beyond an acknowledgement.")

            # Rendering each code block now automatically includes the code type and backticks
            for code_block in assets:
                buf.append(repr(code_block))
            buf.append("---")

        # Add the postamble indicating there is no need for further action beyond acknowledgement
        buf.append("Please acknowledge that these files will now be considered the latest versions for any subsequent tasks.")
        
        # Call the parent's generate method to store the generated request text
        super().generate("\n\n".join(buf))
