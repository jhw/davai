import os
import gnureadline as readline
import logging
import cmd
import difflib
from davai.code_block import CodeBlock, Head, Body
from davai.git import Git
from davai.requests import CodeUpdateRequest, CodeResetRequest, CodeQueryRequest
from davai.responses import CodeResponse, BaseResponse

class BaseCLI(cmd.Cmd):
    HISTORY_FILE = "tmp/cli_history.txt"

    def __init__(self, prompt_name, transport_func):
        super().__init__()
        self.prompt = f"{prompt_name} >>> "
        self.intro = f"Welcome to the {prompt_name} command line interface. Type help or ? to list commands."
        self.git = Git()  # Git instance to handle asset management
        self.git.fetch()  # Load assets from the filesystem into memory
        self.asset_paths = set()  # Initialize the asset_paths set
        self.transport_func = transport_func  # Set the transport function

    def preloop(self):
        # Ensure the directory for the history file exists
        history_dir = os.path.dirname(self.HISTORY_FILE)
        if not os.path.exists(history_dir):
            os.makedirs(history_dir)

        # Load history if the file exists
        if os.path.exists(self.HISTORY_FILE):
            try:
                readline.read_history_file(self.HISTORY_FILE)
                logging.info(f"History loaded from {self.HISTORY_FILE}")
            except FileNotFoundError:
                pass 

    def postloop(self):
        # Save history to the history file
        try:
            readline.write_history_file(self.HISTORY_FILE)
            logging.info(f"History saved to {self.HISTORY_FILE}")
        except FileNotFoundError:
            pass

    def print_diff(self, old_code, new_code):
        """
        Prints a git-like diff between two pieces of code, highlighting changes.
        """
        # Split the code into lines for easier processing
        old_lines = old_code.splitlines(keepends=True)
        new_lines = new_code.splitlines(keepends=True)
        
        # Create a unified diff using difflib
        diff = difflib.unified_diff(old_lines, new_lines, fromfile='old_code', tofile='new_code')
        
        # ANSI escape codes for colors
        GREEN = '\033[92m'
        RED = '\033[91m'
        RESET = '\033[0m'
        
        # Iterate through the diff and print with colors
        for line in diff:
            if line.startswith('+') and not line.startswith('+++'):
                print(f"{GREEN}{line.rstrip()}{RESET}")
            elif line.startswith('-') and not line.startswith('---'):
                print(f"{RED}{line.rstrip()}{RESET}")
            else:
                print(line.rstrip())

    def git_reset_task(self, action):
        """
        A method for handling git-related tasks like fetch, undo, and redo.
        """
        # Dynamically call the appropriate git method
        git_method = getattr(self.git, action, None)
        if callable(git_method):
            git_method()
        else:
            logging.error(f"Invalid action: {action}")
            return

        # Filter assets based on self.asset_paths
        matching_assets = [asset for asset in self.git.assets if asset.head.path in self.asset_paths]
        
        if not matching_assets:
            logging.info("No matching assets found.")
            return

        logging.info(f"Assets for {action}: {', '.join([cb.head.path for cb in matching_assets])}")

        # Generate a CodeResetRequest
        request = CodeResetRequest()
        request.generate(matching_assets)

        # Call the transport function
        response_text = self.transport_func(request.request_text)

        # Handle the response
        response = BaseResponse(response_text)
        response.save()

        logging.info(f"{action.capitalize()} request completed.")

    def do_fetch(self, arg):
        """Fetch and integrate assets based on the asset paths."""
        self.git_reset_task("fetch")

    def do_undo(self, arg):
        """Undo the last git operation and synchronize assets."""
        self.git_reset_task("undo")

    def do_redo(self, arg):
        """Redo the last undone git operation and synchronize assets."""
        self.git_reset_task("redo")

    def do_clear(self, arg):
        """Clear the tracked asset paths."""
        self.asset_paths.clear()
        logging.info("Asset paths have been cleared.")
        
    def do_task(self, arg):
        if not arg:
            logging.error("No input provided for code generation.")
            return
        
        try:
            assets = self.git.assets.match(arg)

            if not assets:
                logging.error("No matching assets found for code generation.")
                return

            logging.info(f"Assets: {', '.join([cb.head.path for cb in assets])}")

            # Update self.asset_paths with the paths of the matched assets
            self.asset_paths.update(assets.paths)

            # Generate the request
            request = CodeUpdateRequest()
            request.generate(arg, assets)

            # Save the request
            request.save()

            # Call the transport function
            response_text = self.transport_func(request.request_text)

            # Handle the response
            response = CodeResponse(response_text)
            response.save()

            # Extract code blocks from the response
            new_assets = response.extract_code_blocks()

            # Process new assets
            for new_asset in new_assets:
                # Check if the asset already exists in git assets
                existing_asset = next((asset for asset in self.git.assets if asset.head.path == new_asset.head.path), None)

                if existing_asset:
                    # If the new asset body is the same as the existing body, skip it
                    if existing_asset.body.code == new_asset.body.code:
                        logging.info(f"No changes detected for asset: {new_asset.head.path}. Skipping update.")
                        continue

                    # Print the diff between the old and new versions
                    print(f"Diff for {new_asset.head.path}:")
                    self.print_diff(existing_asset.body.code, new_asset.body.code)

                    # Query the user for confirmation to integrate the asset
                    user_input = input(f"Integrate {new_asset.head.path}? (y/n): ").strip().lower()
                    if user_input == 'y':
                        logging.info(f"Updating asset: {new_asset.head.path}.")
                        self.git.add_asset(new_asset.head.path, new_asset.body.code)
                    else:
                        logging.info(f"Skipped updating asset: {new_asset.head.path}.")
                else:
                    # If the asset does not exist, add it
                    logging.info(f"Adding new asset: {new_asset.head.path}.")
                    self.git.add_asset(new_asset.head.path, new_asset.body.code)

            # Update self.asset_paths with the paths from the new assets
            self.asset_paths.update(new_assets.paths)
                
            self.git.push()

        except RuntimeError as error:
            logging.error(f"Error: {error}")

    def do_query(self, arg):
        if not arg:
            logging.error("No input provided for code querying.")
            return

        try:
            assets = self.git.assets.match(arg)

            if not assets:
                logging.error("No matching assets found for code querying.")
                return

            logging.info(f"Assets: {', '.join([cb.head.path for cb in assets])}")

            # Update self.asset_paths with the paths of the matched assets
            self.asset_paths.update(assets.paths)

            # Generate the query request
            request = CodeQueryRequest()
            request.generate(arg, assets)

            # Save the request
            request.save()

            # Call the transport function
            response_text = self.transport_func(request.request_text)

            # Handle the response using BaseResponse
            response = BaseResponse(response_text)
            response.save()

            # Print the response text to stdout
            print(response_text)
            logging.info("Query response received and displayed.")

        except RuntimeError as error:
            logging.error(f"Error: {error}")
            
    def do_quit(self, arg):
        logging.info("Goodbye!")
        return True

    def do_exit(self, arg):
        logging.info("Goodbye!")
        return True

    def do_EOF(self, arg):
        logging.info("Goodbye!")
        return True
