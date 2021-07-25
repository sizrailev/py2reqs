"""
Testing the extraction of a list of modules from a Python file or __init__.py

See py2reqs_fixtures.py for details of the test cases.
"""

import unittest
from pathlib import Path

from py2reqs.import_extractor import ImportsExtractor

from .py2reqs_fixtures import PACKAGE1_EXPECTED_MODULES, PACKAGE2_EXPECTED_MODULES, TEST_FILES

TEST_PACKAGE_PATH = Path('package1').resolve()
TEST_PACKAGE2_PATH = Path('package2').resolve()
TEST_PATH_NOT_EXIST = Path('blah/blah')
TEST_PATH_NOT_PYTHON = Path('package1/requirements.txt')
TEST_FILE_PATH_MODULE1 = TEST_PACKAGE_PATH / 'module1.py'
TEST_FILE_PATH_MODULE2 = TEST_PACKAGE_PATH / 'subpackage1' / 'module2.py'
TEST_CWD_PATH = Path('.').resolve()


class TestImportsExtractor(unittest.TestCase):
    def setUp(self) -> None:
        self.maxDiff = None

    def test_init(self):
        # path is not empty
        with self.assertRaises(ValueError) as cm:
            ImportsExtractor('')
        msg = str(cm.exception)
        self.assertRegex(msg, "^Empty path")

        # package root exists
        with self.assertRaises(ValueError) as cm:
            ImportsExtractor(path=TEST_PACKAGE_PATH, package_root=TEST_PATH_NOT_EXIST)
        msg = str(cm.exception)
        self.assertRegex(msg, "^Package root.*does not exist")

        # package root is not a folder
        with self.assertRaises(ValueError) as cm:
            ImportsExtractor(path=TEST_PACKAGE_PATH, package_root=TEST_PATH_NOT_PYTHON)
        msg = str(cm.exception)
        self.assertRegex(msg, "not a folder")

        # package root does not contain path
        with self.assertRaises(ValueError) as cm:
            ImportsExtractor(path=TEST_FILE_PATH_MODULE1, package_root=TEST_PACKAGE2_PATH)
        msg = str(cm.exception)
        self.assertRegex(msg, "not located in")

        # not a python file
        with self.assertRaises(ValueError) as cm:
            ImportsExtractor(path=TEST_PATH_NOT_PYTHON, package_root=TEST_PACKAGE_PATH)
        msg = str(cm.exception)
        self.assertRegex(msg, "Not a Python file")

    def test_get_python_file_path(self):
        # path does not exist
        with self.assertRaises(ValueError) as cm:
            file_path = ImportsExtractor.get_python_file_path(str(TEST_PATH_NOT_EXIST))
        msg = str(cm.exception)
        self.assertRegex(msg, "not exist")

        # not a python file
        with self.assertRaises(ValueError) as cm:
            file_path = ImportsExtractor.get_python_file_path(str(TEST_PATH_NOT_PYTHON))
        msg = str(cm.exception)
        self.assertRegex(msg, "Not a Python file")

        # a folder
        file_path = ImportsExtractor.get_python_file_path(str(TEST_PACKAGE_PATH))
        self.assertRegex(str(file_path), f"{str(TEST_PACKAGE_PATH)}/__init__.py$")

        # a Python file
        file_path = ImportsExtractor.get_python_file_path(str(TEST_FILE_PATH_MODULE1))
        self.assertRegex(str(file_path), f"{str(TEST_FILE_PATH_MODULE1)}$")

    def test_extract(self):
        """
        Run tests on all modules with keys in EXPECTED_MODULES
        """
        for name, expected_modules in PACKAGE1_EXPECTED_MODULES.items():
            if name not in TEST_FILES:
                raise KeyError(f"Test file key {name} not found in TEST_FILES")
            extractor = ImportsExtractor(TEST_FILES[name].path, TEST_PACKAGE_PATH)
            self.assertListEqual(PACKAGE1_EXPECTED_MODULES[name], extractor.modules)

        for name, expected_modules in PACKAGE2_EXPECTED_MODULES.items():
            if name not in TEST_FILES:
                raise KeyError(f"Test file key {name} not found in TEST_FILES")
            extractor = ImportsExtractor(TEST_FILES[name].path, TEST_PACKAGE2_PATH)
            self.assertListEqual(PACKAGE2_EXPECTED_MODULES[name], extractor.modules)


if __name__ == '__main__':
    unittest.main()
