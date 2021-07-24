# relative imports
from . import module3
from .. import subpackage1
from .module4 import foo4
from ..module1 import foo1
from ..subpackage1.module4 import bar4


def foo2():
    bar4()
