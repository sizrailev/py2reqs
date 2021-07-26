import unittest
from pathlib import Path

from py2reqs.imports_collector import ImportsCollector

THIS_FILE_FOLDER = Path(__file__).resolve().parent
PACKAGE_PATH = (THIS_FILE_FOLDER / Path('package1')).resolve()
PACKAGE2_PATH = (THIS_FILE_FOLDER / Path('package2')).resolve()
PATH_NOT_EXIST = THIS_FILE_FOLDER / Path('blah/blah')
FILE_PATH_MODULE1 = THIS_FILE_FOLDER / PACKAGE_PATH / 'module1.py'


class TestImportsCollector(unittest.TestCase):
    def setUp(self) -> None:
        self.maxDiff = None

    def test_init(self):
        collector = ImportsCollector()
        self.assertListEqual(collector.app_dirs, [Path('.').resolve()])

        with self.assertRaises(ValueError) as cm:
            ImportsCollector(app_dirs=[PATH_NOT_EXIST])
        msg = str(cm.exception)
        self.assertRegex(msg, "^Application directory.*does not exist")

        with self.assertRaises(ValueError) as cm:
            ImportsCollector(app_dirs=[FILE_PATH_MODULE1])
        msg = str(cm.exception)
        self.assertRegex(msg, "^Application directory.*not a dir")

    def test_find_path_in_app_dirs(self):
        # Passing paths
        collector = ImportsCollector([PACKAGE_PATH, PACKAGE2_PATH])
        root_folder = collector._find_path_in_app_dirs(source_path=FILE_PATH_MODULE1)
        self.assertEqual(str(PACKAGE_PATH), str(root_folder))

        # passing strings
        collector = ImportsCollector([str(PACKAGE_PATH), str(PACKAGE2_PATH)])
        root_folder = collector._find_path_in_app_dirs(source_path=str(FILE_PATH_MODULE1))
        self.assertEqual(str(PACKAGE_PATH), str(root_folder))

        # source path doesn't exist
        collector = ImportsCollector([PACKAGE_PATH, PACKAGE2_PATH])
        with self.assertRaises(ValueError) as cm:
            collector._find_path_in_app_dirs(source_path=PATH_NOT_EXIST)
        msg = str(cm.exception)
        self.assertRegex(msg, "^Path.*does not exist")

        # not in app_dirs
        collector = ImportsCollector([PACKAGE_PATH, PACKAGE2_PATH])
        root_folder = collector._find_path_in_app_dirs(source_path=__file__)
        self.assertIsNone(root_folder)


if __name__ == '__main__':
    unittest.main()
