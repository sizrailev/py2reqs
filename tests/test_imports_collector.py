import sys
import unittest
from pathlib import Path

from py2reqs.imports_collector import ImportsCollector
from tests.fixtures import EXPECTED_DEPENDENCIES, TEST_FILES

THIS_FILE_FOLDER = Path(__file__).resolve().parent
PACKAGE1_PATH = (THIS_FILE_FOLDER / Path('package1')).resolve()
SUBPACKAGE_PATH = (PACKAGE1_PATH / Path('subpackage1')).resolve()
PACKAGE2_PATH = (THIS_FILE_FOLDER / Path('package2')).resolve()
PATH_NOT_EXIST = THIS_FILE_FOLDER / Path('blah/blah')
FILE_PATH_MODULE1 = THIS_FILE_FOLDER / PACKAGE1_PATH / 'module1.py'
FILE_PATH_MODULE2 = THIS_FILE_FOLDER / PACKAGE1_PATH / 'subpackage1' / 'module2.py'
FILE_PATH_ABSOLUTE_IMPORT = THIS_FILE_FOLDER / PACKAGE1_PATH / 'absolute.py'

# For the package1 and package2 the app folder is py2reqs/tests
APP_DIRS = [THIS_FILE_FOLDER]
APP_DIRS_STR = [str(THIS_FILE_FOLDER)]


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
        # passing paths one level down
        collector = ImportsCollector(APP_DIRS)
        root_folder = collector._find_package_root_in_app_dirs(source_path=FILE_PATH_MODULE1)
        self.assertEqual(str(PACKAGE1_PATH), str(root_folder))

        # two levels down
        collector = ImportsCollector(APP_DIRS)
        root_folder = collector._find_package_root_in_app_dirs(source_path=FILE_PATH_MODULE2)
        self.assertEqual(str(PACKAGE1_PATH), str(root_folder))

        # passing strings
        collector = ImportsCollector(APP_DIRS_STR)
        root_folder = collector._find_package_root_in_app_dirs(source_path=str(FILE_PATH_MODULE1))
        self.assertEqual(str(PACKAGE1_PATH), str(root_folder))

        # source path doesn't exist
        collector = ImportsCollector(APP_DIRS)
        with self.assertRaises(ValueError) as cm:
            collector._find_package_root_in_app_dirs(source_path=PATH_NOT_EXIST)
        msg = str(cm.exception)
        self.assertRegex(msg, "^Path.*does not exist")

        # not in app_dirs
        collector = ImportsCollector(APP_DIRS)
        root_folder = collector._find_package_root_in_app_dirs(source_path=__file__)
        self.assertIsNone(root_folder)

        # same as one of app_dirs
        collector = ImportsCollector(APP_DIRS)
        with self.assertRaises(ValueError) as cm:
            collector._find_package_root_in_app_dirs(source_path=APP_DIRS[0])
        msg = str(cm.exception)
        self.assertRegex(msg, "^Path.*one of the app")

        # file in app dir
        collector = ImportsCollector([PACKAGE1_PATH])
        root_folder = collector._find_package_root_in_app_dirs(source_path=FILE_PATH_MODULE1)
        self.assertIsNone(root_folder)

        # folder in app dir
        collector = ImportsCollector([PACKAGE1_PATH])
        root_folder = collector._find_package_root_in_app_dirs(source_path=SUBPACKAGE_PATH)
        self.assertEqual(str(SUBPACKAGE_PATH), str(root_folder))

    def test_collect_dependencies(self):
        # add app dirs to path since the `tests` folder is not in PYTHONPATH
        for folder in APP_DIRS:
            sys.path.insert(0, str(folder))
        collector = ImportsCollector(APP_DIRS)
        collector.collect_dependencies(FILE_PATH_MODULE1)
        self.assertEqual(5, len(collector.local_module_paths))
        # dependencies include the source_path
        self.assertEqual(6, len(collector.dependencies))
        self.assertSetEqual({'package1'}, collector.local)
        self.assertSetEqual(set(), collector.third_party)

        collector2 = ImportsCollector(APP_DIRS)
        collector2.collect_dependencies(FILE_PATH_ABSOLUTE_IMPORT)
        self.assertEqual(1, len(collector2.dependencies))
        self.assertSetEqual(set(), collector2.local)
        self.assertSetEqual({'pandas'}, collector2.third_party)

        for key in EXPECTED_DEPENDENCIES.keys():
            collector3 = ImportsCollector(APP_DIRS)
            source_path = THIS_FILE_FOLDER / TEST_FILES[key].path
            collector3.collect_dependencies(source_path)
            expected_dependencies = [
                str((THIS_FILE_FOLDER / TEST_FILES[d].path).resolve()) for d in EXPECTED_DEPENDENCIES[key]
            ]
            actual_dependencies = [str(d) for d in collector3.dependencies.keys()]
            self.assertListEqual(sorted(expected_dependencies), sorted(actual_dependencies))


if __name__ == '__main__':
    unittest.main()
