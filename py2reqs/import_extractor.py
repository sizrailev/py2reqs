import ast
from pathlib import Path, PurePath
from typing import List, Optional, Union

from py2reqs.utils import get_module_from_path, get_module_parents, get_python_file_path


class ImportsExtractor(ast.NodeVisitor):
    """
    Extract a list of imports from a Python file or a folder's __init__.py file,
    including each imported module's packages and subpackages.
    The package root folder must contain the file and is necessary to resolve relative imports.
    The default package root is the current working directory.
    The results are stored in the "modules" list.
    """

    def __init__(self, path: Union[str, Path], package_root: Optional[Union[str, Path]] = None) -> None:
        if not path:
            raise ValueError("Empty path.")
        path = Path(path).resolve()

        self.package_root = Path(package_root or '.').resolve()
        if not self.package_root.exists():
            raise ValueError(f"Package root folder {package_root} does not exist.")

        if not self.package_root.is_dir():
            raise ValueError(f"Package root '{package_root}' is not a folder.")

        if not (path.samefile(self.package_root) or str(self.package_root) in str(path.resolve())):
            raise ValueError(f"Path '{path}' is not located in the package root '{package_root}'.")

        self.file_path: Path = get_python_file_path(path)
        self.full_module_name = get_module_from_path(self.file_path, self.package_root)
        self.imports: List[ast.Import] = []
        self.importsFrom: List[ast.ImportFrom] = []
        self.modules: List[str] = []

        ast_file = ast.parse(self.file_path.read_text())
        self.visit(ast_file)
        self.add_module_parents()

    def visit_Import(self, node: ast.Import) -> None:
        self.imports.append(node)

        # absolute imports - ignore indentation and just get all module names
        for name in node.names:
            self.modules.append(name.name)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.importsFrom.append(node)

        if not node.level:
            # absolute import: from subpackage1 import object1
            assert node.module is not None  # true for node.level == 0
            # This module can be either local in the same folder, or from another package.
            # We check if there's a local folder or a file matching the name of the module
            parts = node.module.split('.')
            local_path = Path(*parts)
            maybe_folder = Path(self.file_path.parent / local_path).resolve()
            maybe_file = Path(self.file_path.parent / (str(local_path) + '.py')).resolve()
            if maybe_folder.exists() or maybe_file.exists():
                # local module, prepend the package root
                self.modules.append(
                    '.'.join(list(self.file_path.parent.relative_to(self.package_root.parent).parts) + [node.module])
                )
            else:
                # global module, save as is
                self.modules.append(node.module)
        elif not node.module:
            # relative import: from .. import subpackage1
            self.modules.append(
                '.'.join(
                    list(self.file_path.parents[node.level - 1].relative_to(self.package_root.parent).parts)
                    + [node.names[0].name]
                )
            )
        else:
            # relative import: from ..subpackage1 import module5
            self.modules.append(
                '.'.join(
                    list(self.file_path.parents[node.level - 1].relative_to(self.package_root.parent).parts)
                    + [node.module]
                )
            )

    def add_module_parents(self):
        """
        Adds missing module parents to the list of modules.
        """
        for module in self.modules:
            parents = get_module_parents(module)
            missing_parents = [p for p in parents if p not in self.modules]
            self.modules.extend(missing_parents)
