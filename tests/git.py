import unittest
import os
import shutil
from davai.git import Git

class GitTest(unittest.TestCase):
    TMP_DIR = "tmp/src"

    def setUp(self):
        """Create the necessary directories and set up the environment before each test."""
        if not os.path.exists(self.TMP_DIR):
            os.makedirs(self.TMP_DIR)
        self.git = Git(self.TMP_DIR)

    def tearDown(self):
        """Clean up the environment after each test."""
        if os.path.exists("tmp"):
            shutil.rmtree("tmp")

    def create_file(self, relative_path, content):
        """Helper method to create a file with the given content."""
        filepath = os.path.join(self.TMP_DIR, relative_path)
        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(filepath, 'w') as file:
            file.write(content)

    def test_add_asset(self):
        self.create_file("file1.txt", "Hello World!")
        self.git.fetch()

        # Assert that the asset was added correctly
        self.assertEqual(len(self.git.assets), 1)
        self.assertEqual(self.git.assets[0].head.path, os.path.join(self.TMP_DIR, "file1.txt"))
        self.assertEqual(self.git.assets[0].body.code, "Hello World!")

    def test_update_asset(self):
        self.create_file("file1.txt", "Hello World!")
        self.git.fetch()

        # Update the content of the file
        self.create_file("file1.txt", "Updated Hello World!")
        self.git.fetch()

        # Assert that the asset was updated
        self.assertEqual(len(self.git.assets), 1)
        self.assertEqual(self.git.assets[0].body.code, "Updated Hello World!")

    def test_remove_asset(self):
        self.create_file("file1.txt", "Hello World!")
        self.git.fetch()
        self.git.remove_asset(os.path.join(self.TMP_DIR, "file1.txt"))

        # Assert that the asset was removed
        self.assertEqual(len(self.git.assets), 0)

    def test_commit(self):
        self.create_file("file1.txt", "Hello World!")
        self.git.fetch()
        self.git.commit("Initial commit")

        # Assert that the commit was recorded
        self.assertEqual(len(self.git.commits), 1)
        self.assertEqual(self.git.commits[0][1], "Initial commit")
        self.assertEqual(len(self.git.commits[0][0]), 1)  # One asset in the snapshot

    def test_undo_redo(self):
        self.create_file("file1.txt", "Hello World!")
        self.git.fetch()
        self.git.commit("Initial commit")

        self.create_file("file2.txt", "Another file content")
        self.git.fetch()
        self.git.commit("Added file2.txt")

        self.git.undo()
        # Assert that the head moves back and file2.txt is no longer present
        self.assertEqual(len(self.git.assets), 1)
        self.assertEqual(self.git.assets[0].head.path, os.path.join(self.TMP_DIR, "file1.txt"))

        self.git.redo()
        # Assert that the redo restores file2.txt
        self.assertEqual(len(self.git.assets), 2)
        self.assertEqual(self.git.assets[1].head.path, os.path.join(self.TMP_DIR, "file2.txt"))

    def test_fetch(self):
        self.create_file("file1.txt", "Hello World!")
        self.create_file("subdir/file2.txt", "Second file content")
        self.git.fetch()

        # Assert that both files were fetched
        self.assertEqual(len(self.git.assets), 2)
        paths = [asset.head.path for asset in self.git.assets]
        self.assertIn(os.path.join(self.TMP_DIR, "file1.txt"), paths)
        self.assertIn(os.path.join(self.TMP_DIR, "subdir/file2.txt"), paths)

    def test_push(self):
        self.create_file("file1.txt", "Hello World!")
        self.git.fetch()

        # Change the content of file1.txt and push it
        self.git.assets[0].body.code = "Updated Hello World!"
        self.git.push()

        # Assert that the file system reflects the updated content
        with open(os.path.join(self.TMP_DIR, "file1.txt"), 'r') as file:
            self.assertEqual(file.read(), "Updated Hello World!")

    def test_clean(self):
        self.create_file("file1.txt", "Hello World!")
        self.git.fetch()

        # Remove the file from the filesystem
        os.remove(os.path.join(self.TMP_DIR, "file1.txt"))
        self.git.clean()

        # Assert that the asset was removed from memory
        self.assertEqual(len(self.git.assets), 0)

    def test_prune(self):
        self.create_file("file1.txt", "Hello World!")
        self.create_file("file2.txt", "Second file content")
        self.git.fetch()

        # Remove file2.txt from the assets manually
        self.git.remove_asset(os.path.join(self.TMP_DIR, "file2.txt"))
        self.git.prune()

        # Assert that file2.txt was removed from the filesystem
        self.assertFalse(os.path.exists(os.path.join(self.TMP_DIR, "file2.txt")))

if __name__ == "__main__":
    unittest.main()
