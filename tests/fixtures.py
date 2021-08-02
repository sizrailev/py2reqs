"""
Testing the conversion of relative imports to absolute

Files/modules:
    package1/
    package1/__init__.py
    package1/module1.py
    package1/requirements.txt
    package1/subpackage1/__init__.py
    package1/subpackage1/module2.py
    package1/subpackage1/module3.py
    package1/subpackage1/module4.py
    package2/
    package2/__init__.py
    package2/module10.py

"""
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union


@dataclass
class TestFile:
    """
    A representation of a file for testing. When content is None, it means it's a folder.
    When content is an empty string, it means it's an empty file.
    This structure can be used for both reading and writing files.
    """

    path: Path
    content: Optional[str] = None


PACKAGE1_EXPECTED_MODULES: Dict[str, List[str]] = {
    'package1_init': ['package1.subpackage1.module4', 'package1', 'package1.subpackage1'],
    'package1_absolute': ['os', 'pandas'],
    'package1_indented': ['this', 'that'],
    'package1_absolute_from': ['os', 'pandas'],
    'package1_module1': ['package1.subpackage1', 'package1.subpackage1.module2', 'package1'],
    'package1_subpackage1_init': ['package1.subpackage1.module3', 'package1', 'package1.subpackage1'],
    'package1_module2': [
        'package1.subpackage1.module3',
        'package1.subpackage1',
        'package1.subpackage1.module4',
        'package1.module1',
        'package1.subpackage1.module4',
        'package1',
    ],
    'package1_module3': [],
    'package1_module4': [],
}

PACKAGE2_EXPECTED_MODULES: Dict[str, List[str]] = {
    'package2_init': [],
    'package2_module10': ['package1.subpackage1', 'package1'],
}

EXPECTED_DEPENDENCIES: Dict[str, List[str]] = dict()

PACKAGE1_INIT = """\
from .subpackage1.module4 import foo4
"""

EXPECTED_DEPENDENCIES['package1_init'] = [
    'package1_init',
    'package1_subpackage1_init',
    'package1_module3',  # imported by subpackage1
    'package1_module4',  # imported by package1
]

SUBPACKAGE1_INIT = """\
from .module3 import foo3 as bar3


def foo():
    bar3()
"""

EXPECTED_DEPENDENCIES['package1_subpackage1_init'] = [
    'package1_init',
    'package1_subpackage1_init',
    'package1_module3',  # imported by subpackage1
    'package1_module4',  # imported by package1
]

ABSOLUTE_IMPORTS = """\
import os
import pandas
"""

ABSOLUTE_IMPORTS_INDENTED = """\
try:
    import this as foo
except ImportError:
    import that as foo
"""

ABSOLUTE_IMPORTS_FROM = """\
from os import getcwd
from pandas import DataFrame
"""

MODULE1 = """\
# import subpackage.__init__.py and trigger relative imports in module2
from subpackage1 import foo
from subpackage1.module2 import foo2


def foo1():
    foo()
    foo2()
"""

EXPECTED_DEPENDENCIES['package1_module1'] = [
    'package1_init',
    'package1_subpackage1_init',
    'package1_module1',
    'package1_module2',
    'package1_module3',
    'package1_module4',
]

MODULE2_RELATIVE_IMPORTS_FROM = """\
# relative imports
from . import module3
from .. import subpackage1
from .module4 import foo4
from ..module1 import foo1
from ..subpackage1.module4 import bar4


def foo2():
    bar4()
"""

EXPECTED_DEPENDENCIES['package1_module2'] = [
    'package1_init',
    'package1_subpackage1_init',
    'package1_module1',
    'package1_module2',
    'package1_module3',
    'package1_module4',
]

MODULE3 = """\
# imported by module2 and subpackage1/__init__.py
def foo3():
    pass
"""

EXPECTED_DEPENDENCIES['package1_module3'] = [
    'package1_init',
    'package1_subpackage1_init',
    'package1_module3',
    'package1_module4',  # imported by package1
]

MODULE4 = """\
# imported by module2 and package1/__init__.py
def foo4():
    pass


def bar4():
    pass
"""

EXPECTED_DEPENDENCIES['package1_module4'] = [
    'package1_init',
    'package1_subpackage1_init',
    'package1_module3',  # imported by subpackage1
    'package1_module4',
]

MODULE10 = """\
# package1 can be a 3rd party or same party to package2
from package1.subpackage1 import foo4


def foo10():
    foo4()
"""

EXPECTED_DEPENDENCIES['package2_module10'] = [
    'package1_init',
    'package1_subpackage1_init',
    'package1_module3',  # imported by subpackage1
    'package1_module4',  # imported by package1
    'package2_module10',
]

REQUIREMENTS = """\
pandas
"""

TEST_FILES: Dict[str, TestFile] = {
    'package1': TestFile(Path('package1'), content=None),
    'package1_init': TestFile(Path('package1') / '__init__.py', content=PACKAGE1_INIT),
    'package1_requirements': TestFile(Path('package1') / 'requirements.txt', content=REQUIREMENTS),
    'package1_absolute': TestFile(Path('package1') / 'absolute.py', content=ABSOLUTE_IMPORTS),
    'package1_indented': TestFile(Path('package1') / 'absolute_indented.py', content=ABSOLUTE_IMPORTS_INDENTED),
    'package1_absolute_from': TestFile(Path('package1') / 'absolute_from.py', content=ABSOLUTE_IMPORTS_FROM),
    'package1_module1': TestFile(Path('package1') / 'module1.py', content=MODULE1),
    'package1_subpackage1': TestFile(Path('package1') / 'subpackage1', content=None),
    'package1_subpackage1_init': TestFile(Path('package1') / 'subpackage1' / '__init__.py', content=SUBPACKAGE1_INIT),
    'package1_module2': TestFile(
        Path('package1') / 'subpackage1' / 'module2.py', content=MODULE2_RELATIVE_IMPORTS_FROM
    ),
    'package1_module3': TestFile(Path('package1') / 'subpackage1' / 'module3.py', content=MODULE3),
    'package1_module4': TestFile(Path('package1') / 'subpackage1' / 'module4.py', content=MODULE4),
    'package2': TestFile(Path('package2'), content=None),
    'package2_init': TestFile(Path('package2') / '__init__.py', content=""),
    'package2_module10': TestFile(Path('package2') / 'module10.py', content=MODULE10),
}


def create_test_files(in_folder: Union[str, Path]):
    """Create all test files in the provided folder."""
    folder = Path(in_folder).resolve()
    if not folder.exists():
        print(f"Creating '{folder}'")
        folder.mkdir()
    elif not folder.is_dir():
        raise ValueError(f"in_folder argument '{in_folder}' is not a folder.")

    for short_name, test_file in TEST_FILES.items():
        file_path = folder / test_file.path
        print(f"short_name: {short_name}, path: {file_path}")
        if test_file.content is None:
            file_path.mkdir(parents=True, exist_ok=True)
        else:
            file_path.write_text(test_file.content)


if __name__ == '__main__':
    create_test_files('.')
