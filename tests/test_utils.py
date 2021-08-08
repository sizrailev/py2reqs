import os
import unittest
from pathlib import Path

from py2reqs.utils import get_module_from_path, get_module_parents, get_python_file_path

# TODO: move common constants to fixtures.py
THIS_FILE_FOLDER = Path(__file__).resolve().parent
PACKAGE_PATH = (THIS_FILE_FOLDER / Path('package1')).resolve()
PATH_NOT_EXIST = THIS_FILE_FOLDER / Path('blah/blah')
PATH_NOT_PYTHON = THIS_FILE_FOLDER / Path('package1/requirements.txt')
FILE_PATH_MODULE1 = THIS_FILE_FOLDER / PACKAGE_PATH / 'module1.py'


class TestUtils(unittest.TestCase):
    def test_get_python_file_path(self):
        # path does not exist
        with self.assertRaises(ValueError) as cm:
            _ = get_python_file_path(str(PATH_NOT_EXIST))
        msg = str(cm.exception)
        self.assertRegex(msg, "not exist")

        # not a python file
        with self.assertRaises(ValueError) as cm:
            _ = get_python_file_path(str(PATH_NOT_PYTHON))
        msg = str(cm.exception)
        self.assertRegex(msg, "Not a Python file")

        # a folder
        file_path = get_python_file_path(str(PACKAGE_PATH))
        self.assertRegex(str(file_path), f"{str(PACKAGE_PATH)}/__init__.py$")

        # a Python file
        file_path = get_python_file_path(str(FILE_PATH_MODULE1))
        self.assertRegex(str(file_path), f"{str(FILE_PATH_MODULE1)}$")

    def test_get_module_parents(self):
        module_name = 'a.b.c.d'
        expected = ['a', 'a.b', 'a.b.c']
        self.assertListEqual(expected, get_module_parents(module_name))

        module_name = 'a.b'
        expected = ['a']
        self.assertListEqual(expected, get_module_parents(module_name))

        module_name = 'a'
        expected = []
        self.assertListEqual(expected, get_module_parents(module_name))

    def test_get_module_from_path(self):
        module = get_module_from_path('package1/module1.py', 'package1')
        self.assertEqual('package1.module1', module)

        module = get_module_from_path('package1/module1.py', 'package1')
        self.assertEqual('package1.module1', module)

        module = get_module_from_path('tests/package1/module1.py', 'tests/package1')
        self.assertEqual('package1.module1', module)

        module = get_module_from_path('tests/package1', 'tests')
        self.assertEqual('tests.package1', module)

        module = get_module_from_path('tests/package1/__init__.py', 'tests/package1')
        self.assertEqual('package1', module)

        os.chdir('tests')
        module = get_module_from_path('fixtures.py', '.')
        self.assertEqual('tests.fixtures', module)


if __name__ == '__main__':
    unittest.main()
