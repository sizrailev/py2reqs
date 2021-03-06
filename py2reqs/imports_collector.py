"""
Given a Python file, recursively traverse its local dependencies,
to classify and record all dependencies.

For each import, classify the import into local, 3rd party, or system.
Locate local dependency files and recursively extract their dependencies.
"""

from pathlib import Path
from typing import Dict, List, Optional, Set, Union

from aspy.refactor_imports.classify import ImportType, _get_module_info, classify_import

from py2reqs.imports_extractor import ImportsExtractor
from py2reqs.utils import get_python_file_path


class ImportsCollector:
    """
    Recursively collects Python imports.
    Maintains a list of dependencies, paths, source files, 3rd party dependencies, etc.
    """

    def __init__(self, app_dirs: Optional[List[Union[str, Path]]] = None, verbose: bool = False) -> None:
        """
        Constructor initializes the collections.
        :param app_dirs: a list of top-level application folders, default: ('.',)
        :param verbose: when True, prints out all visited modules and files.
        """
        # TODO: maybe... check if app_dirs is a string and either raise an exception or convert it to list
        app_dirs = app_dirs or ['.']
        self.app_dirs = []
        for folder in app_dirs:
            path = Path(folder).resolve()
            if not path.exists():
                raise ValueError(f"Application directory '{folder}' does not exist.")
            if not path.is_dir():
                raise ValueError(f"Application directory '{folder}' is not a directory.")
            self.app_dirs.append(path)

        self.third_party: Set[str] = set()  # 3rd party top-level modules
        self.builtins: Set[str] = set()  # built-in top-level modules
        self.local: Set[str] = set()  # top-level modules within app_dirs
        self.files_to_visit: Set[str] = set()  # a queue of application module files to visit
        self.source_files: Set[str] = set()  # files for which the dependencies are collected
        self.visited_files: Set[str] = set()  # application module files that have been visited
        self.dependencies: Dict[str, List[str]] = dict()  # a map of file dependencies on modules
        self.local_module_paths: Dict[str, str] = dict()  # a map of local modules to their resolved paths
        self._verbose: bool = verbose

    def _find_package_root_in_app_dirs(self, source_path: Union[str, Path]) -> Optional[Path]:
        """
        Checks if the source path for a module is in a package within any of the app_dirs
        and returns the package root path or None if it wasn't found.
        For example, if the package structure is `app/package1/module1.py` and `app/script1.py`
        and `app` is in the `app_dirs`, module1 is inside the package1 package and the
        package root is `app/package1`, whereas script1 is not in a package, so the package root
        will be None.
        """
        path = Path(source_path).resolve()
        if not path.exists():
            raise ValueError(f"Path '{path}' does not exist.")

        for folder in self.app_dirs:
            if str(folder) in str(path):
                # source_path is inside one of the app_dirs
                relative_path = path.relative_to(folder)
                if str(relative_path) == '.':
                    # path and folder are the same - should not happen
                    raise ValueError(f"Path {source_path} is one of the application directories.")
                if len(relative_path.parts) == 1:
                    # path is in the folder
                    if path.is_file():
                        # a file in the app dir => no package root
                        return None
                    elif path.is_dir():
                        # a folder in the app dir => the package root is path
                        return path
                else:
                    return Path(folder).resolve() / relative_path.parts[0]
        return None

    def process_path(self, path: Union[str, Path]) -> None:
        """
        Given the path, extracts imports using ImportsExtractor and
        calls process_modules on every found module.
        """
        path = Path(path).resolve()
        root_folder = self._find_package_root_in_app_dirs(path)
        extractor = ImportsExtractor(path, package_root=root_folder)
        self.dependencies[str(path)] = sorted(list(set(extractor.modules)))
        for module in extractor.modules:
            self.process_module(module)
        self.visited_files.add(str(get_python_file_path(path)))

    def collect_dependencies(self, source_path: Union[str, Path]) -> None:
        """
        The main entry point for the class. The source path is a Python file
        or a folder. In the latter case, it is converted in __init__.py file.
        To process multiple files or all files in a folder, call this function
        for each individual file.
        """
        self.source_files.add(str(get_python_file_path(source_path)))
        self.process_path(source_path)
        while len(self.files_to_visit):
            self.process_path(self.files_to_visit.pop())

    def _add_local_module(self, full_module_name: str) -> None:
        """
        Retrieve the file containing the module and add it to the queue for visits.
        """
        app_dirs = tuple([str(d) for d in self.app_dirs])
        found, module_path, is_builtin = _get_module_info(
            full_module_name,
            application_dirs=app_dirs,
        )
        module_path = get_python_file_path(module_path)
        if str(module_path) not in self.visited_files:
            if self._verbose:
                print(f"Module path: {module_path}")
            self.files_to_visit.add(str(module_path))
            self.local_module_paths[full_module_name] = str(module_path)

    def process_module(self, full_module_name: str) -> None:
        """
        Depending on the module type, add it to the list of third party packages or,
        for the application modules, put the file containing the module in the list of files to visit.
        """
        if self._verbose:
            print(f"Processing module {full_module_name}")
        top_module_name, _, _ = full_module_name.partition('.')
        app_dirs = tuple([str(d) for d in self.app_dirs])
        import_type = classify_import(top_module_name, app_dirs)

        if self._verbose:
            print(f"Full name: {full_module_name}; Top name: {top_module_name}; Type: {str(import_type)}")

        if import_type == ImportType.THIRD_PARTY:
            self.third_party.add(top_module_name)
        elif import_type == ImportType.APPLICATION:
            self._add_local_module(full_module_name)
            self.local.add(top_module_name)
        elif import_type in (ImportType.BUILTIN, ImportType.FUTURE):
            self.builtins.add(top_module_name)
        else:
            # shouldn't happen, adding in case more types are added
            raise ValueError(f"Unknown import type {import_type}")
