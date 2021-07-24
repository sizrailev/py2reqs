# import subpackage.__init__.py and trigger relative imports in module2
from subpackage1 import foo
from subpackage1.module2 import foo2


def foo1():
    foo()
    foo2()
