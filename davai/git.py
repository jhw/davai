import os
import logging
from davai.code_block import Head, Body, CodeBlock
from davai.assets import Assets

class Git:
    def __init__(self, root = "src"):
        self.root = root
        self.assets = Assets()  # A list to hold CodeBlock objects
        self.commits = []  # List of commits (snapshots of assets)
        self.head = -1  # Index of the current commit (-1 means no commits yet)
        self.redo_stack = []  # Stack for redo operations


    def add_asset(self, filename, content):
        """Adds or updates an asset (file)."""
        head = Head(filename)
        body = Body(content)
        new_code_block = CodeBlock(head, body)

        # Check if the file is already in assets, if so update it
        for i, asset in enumerate(self.assets):
            if asset.head.path == filename:
                self.assets[i] = new_code_block
                logging.info(f"Updated asset: {filename}")
                return
        
        # If it's a new asset, add it to the assets list
        self.assets.append(new_code_block)
        logging.info(f"Added asset: {filename}")

    def remove_asset(self, filename):
        """Removes an asset (file)."""
        self.assets = [asset for asset in self.assets if asset.head.path != filename]
        logging.info(f"Removed asset: {filename}")

    def commit(self, message):
        """Commits the current state of assets."""
        snapshot = self.assets.copy()  # Copy the current state of the assets
        self.commits = self.commits[:self.head + 1]  # Discard any redo history
        self.commits.append((snapshot, message))  # Save the snapshot with a message
        self.head += 1  # Move the head to the latest commit
        self.redo_stack = []  # Clear the redo stack
        logging.info(f"Commit {self.head}: {message}")

    def undo(self):
        """Moves the head back by one commit (undo)."""
        if self.head > 0:
            self.redo_stack.append(self.commits[self.head])
            self.head -= 1
            self.assets = self.commits[self.head][0].copy()  # Restore assets from the previous commit
            logging.info(f"Undo: Moved to commit {self.head}")
        else:
            logging.info("No more commits to undo.")

    def redo(self):
        """Moves the head forward by one commit (redo)."""
        if self.redo_stack:
            redo_commit = self.redo_stack.pop()
            self.head += 1
            self.commits.append(redo_commit)
            self.assets = redo_commit[0].copy()  # Restore assets from the redo commit
            logging.info(f"Redo: Moved to commit {self.head}")
        else:
            logging.info("No commits to redo.")

    def log(self):
        """Shows the commit history."""
        for i, (snapshot, message) in enumerate(self.commits):
            current = " <-- HEAD" if i == self.head else ""
            logging.info(f"Commit {i}: {message}{current}")

    def show_assets(self):
        """Displays the current state of assets."""
        logging.info("Current assets:")
        for asset in self.assets:
            logging.info(f"  {asset.head.path}: {repr(asset.body)}")

    def fetch(self):
        """Recursively fetches files from the root directory and adds them as assets."""
        if os.path.exists(self.root):
            for dirpath, _, filenames in os.walk(self.root):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    with open(filepath, 'r') as file:
                        content = file.read()
                        # Use absolute path with root for consistency
                        relative_path = os.path.relpath(filepath, self.root)
                        full_path = os.path.join(self.root, relative_path)
                        self.add_asset(full_path, content)
        else:
            logging.info(f"Root directory '{self.root}' does not exist.")

    def push(self):
        """Saves assets to the file system, creating directories if necessary.
        Only writes the file if it's new or if the contents have changed.
        """
        for asset in self.assets:
            filename = asset.head.path
            content = asset.body.code
            
            # Ensure the filename is relative to the root
            if not filename.startswith(self.root):
                continue
            
            relative_filename = os.path.relpath(filename, self.root)
            filepath = os.path.join(self.root, relative_filename)
            directory = os.path.dirname(filepath)
            
            # Check if the file exists and has the same content
            if os.path.exists(filepath):
                with open(filepath, 'r') as existing_file:
                    existing_content = existing_file.read()
                    if existing_content == content:
                        continue  # Skip if content is the same

            # If the file doesn't exist or the content has changed, write the file
            if not os.path.exists(directory):
                os.makedirs(directory)  # Create directories if they don't exist
                logging.info(f"Created directory: {directory}")

            with open(filepath, 'w') as file:
                file.write(content)
                logging.info(f"Written file: {filepath}")

    def clean(self):
        """Removes assets from memory if the corresponding file doesn't exist on the filesystem."""
        to_remove = []
        for asset in self.assets:
            filename = asset.head.path
            filepath = os.path.join(self.root, os.path.relpath(filename, self.root))
            if not os.path.exists(filepath):
                to_remove.append(asset)

        for asset in to_remove:
            self.remove_asset(asset.head.path)
            logging.info(f"Purged asset: {asset.head.path}, as it doesn't exist in the filesystem.")

    def prune(self):
        """Removes files from the root directory if they are not present in the in-memory assets."""
        if os.path.exists(self.root):
            for dirpath, _, filenames in os.walk(self.root):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    relative_path = os.path.relpath(filepath, self.root)
                    full_path = os.path.join(self.root, relative_path)
                    if full_path not in [asset.head.path for asset in self.assets]:
                        os.remove(filepath)  # Delete the file from the filesystem
                        logging.info(f"Deleted file: {filepath} (not found in assets)")
        else:
            logging.info(f"Root directory '{self.root}' does not exist.")

if __name__ == "__main__":
    # Example usage:
    git = Git()

    # Add and commit assets
    git.add_asset("tmp/hello-git/file1.txt", "Hello World!")
    git.commit("Initial commit")

    git.add_asset("tmp/hello-git/subdir/file2.txt", "Second file content")
    git.commit("Added file2.txt")

    git.add_asset("tmp/hello-git/file1.txt", "Updated Hello World!")
    git.commit("Updated file1.txt")

    git.log()
    git.show_assets()

    # Simulate a push and then prune
    git.push("tmp/hello-git")  # Push assets to output_directory

    # Remove files in "output_directory" that are not present in the assets
    git.prune("tmp/hello-git")

    git.show_assets()

    # Undo and Redo
    git.undo()
    git.show_assets()

    git.redo()
    git.show_assets()
