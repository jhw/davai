import unittest
import os
import sys
import importlib.util

def discover_and_run_tests(test_dir="tests"):
    """
    Discover and run all test cases in the specified directory.
    Recursively finds all classes extending unittest.TestCase and executes them.
    """
    # Ensure the test directory is in the Python path
    sys.path.insert(0, os.path.abspath(test_dir))
    
    # Test suite to hold all tests
    suite = unittest.TestSuite()

    # Recursively walk through the test directory
    for root, _, files in os.walk(test_dir):
        for file in files:
            # Only consider Python files
            if file.endswith(".py"):
                test_file = os.path.join(root, file)

                # Import the module dynamically
                module_name = os.path.splitext(os.path.relpath(test_file, test_dir))[0].replace(os.sep, ".")
                spec = importlib.util.spec_from_file_location(module_name, test_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Iterate through attributes in the module to find TestCase classes
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, unittest.TestCase):
                        # Add the discovered test case class to the test suite
                        tests = unittest.defaultTestLoader.loadTestsFromTestCase(attr)
                        suite.addTests(tests)

    # Run the test suite and output the results
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return whether the tests were successful
    return result.wasSuccessful()

if __name__ == "__main__":
    # Run the tests and exit with the appropriate status code
    success = discover_and_run_tests()
    sys.exit(0 if success else 1)
