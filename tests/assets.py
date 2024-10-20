import unittest
import os
from davai.code_block import CodeBlock, Head, Body
from davai.assets import Assets

class AssetsTest(unittest.TestCase):
    def setUp(self):
        """Set up a few CodeBlock assets for testing."""
        self.assets = Assets()

        # Create dummy CodeBlocks
        code1 = CodeBlock(Head("src/App.js"), Body("console.log('Hello World');"))
        code2 = CodeBlock(Head("src/styles.css"), Body("body { background-color: black; }"))
        code3 = CodeBlock(Head("src/Content.ts"), Body("export const content = 'TypeScript content';"))
        code4 = CodeBlock(Head("src/DeleteModal.js"), Body("function deleteModal() { return true; }"))

        # Add them to Assets
        self.assets.extend([code1, code2, code3, code4])

    def test_paths(self):
        """Test if the paths property returns the correct list of paths."""
        expected_paths = ["src/App.js", "src/styles.css", "src/Content.ts", "src/DeleteModal.js"]
        self.assertEqual(self.assets.paths, expected_paths)

    def test_match_exact(self):
        """Test if match method returns exact matches correctly."""
        matched_assets = self.assets.match("App")
        self.assertEqual(len(matched_assets), 1)
        self.assertEqual(matched_assets[0].head.path, "src/App.js")

    def test_match_partial(self):
        """Test if match method returns partial matches correctly."""
        matched_assets = self.assets.match("delete")
        self.assertEqual(len(matched_assets), 1)
        self.assertEqual(matched_assets[0].head.path, "src/DeleteModal.js")

    def test_match_case_insensitive(self):
        """Test if match method is case-insensitive."""
        matched_assets = self.assets.match("app")
        self.assertEqual(len(matched_assets), 1)
        self.assertEqual(matched_assets[0].head.path, "src/App.js")

    def test_no_matches(self):
        """Test if match method returns an empty Assets instance when there are no matches."""
        matched_assets = self.assets.match("nonexistent")
        self.assertEqual(len(matched_assets), 0)

if __name__ == '__main__':
    unittest.main()
