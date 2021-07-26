"""
Given a Python file, recursively traverse its local dependencies,
to classify and record all dependencies.

For each import, classify the import into local, 3rd party, or system.
Locate local dependency files and recursively extract their dependencies.
"""

from pathlib import Path
from typing import List, Optional, Set, Union

from aspy.refactor_imports.classify import ImportType, _get_module_info, classify_import

from py2reqs.import_extractor import ImportsExtractor


class ImportsCollector:
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
        self.visited_files: Set[str] = set()  # application module files that have been visited
        self._verbose: bool = verbose

    def _find_path_in_app_dirs(self, source_path: Union[str, Path]) -> Optional[Path]:
        """
        Checks if the source path is in any of the app_dirs and returns the application directory path
        or None if it wasn't found.
        """
        path = Path(source_path).resolve()
        if not path.exists():
            raise ValueError(f"Path '{path}' does not exist.")

        for folder in self.app_dirs:
            if str(folder) in str(path):
                # source_path is inside one of the app_dirs
                return Path(folder).resolve()
        return None

    def collect_dependencies(self, source_path: Union[str, Path]) -> None:
        root_folder = self._find_path_in_app_dirs(source_path)

    def _add_module(self, full_module_name: str) -> None:
        """
        Retrieve the file containing the module and add it to the queue for visits.
        """
        app_dirs = tuple([str(self.app_dirs) for d in self.app_dirs])
        found, module_path, is_builtin = _get_module_info(
            full_module_name,
            application_dirs=app_dirs,
        )
        if module_path not in self.visited_files:
            if self._verbose:
                print(f"Module path: {module_path}")
            self.files_to_visit.add(module_path)

    def process_module(self, full_module_name: str) -> None:
        """
        Depending on the module type, add it to the list of third party packages or,
        for the application modules, put the file containing the module in the list of files to visit.
        """
        if self._verbose:
            print(f"Processing module {full_module_name}")
        top_module_name, _, _ = full_module_name.partition('.')
        app_dirs = tuple([str(self.app_dirs) for d in self.app_dirs])
        import_type = classify_import(top_module_name, app_dirs)

        if self._verbose:
            print(f"Full name: {full_module_name}; Top name: {top_module_name}; Type: {str(import_type)}")

        if import_type == ImportType.THIRD_PARTY:
            self.third_party.add(top_module_name)
        elif import_type == ImportType.APPLICATION:
            self._add_module(full_module_name)
