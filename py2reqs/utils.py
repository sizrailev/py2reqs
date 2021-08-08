"""
Helper functions
"""
from pathlib import Path, PurePath
from typing import List, Union


def get_python_file_path(path: Union[str, Path]) -> Path:
    """
    Convert the path of a Python file or folder to an absolute path of the file
    """
    file_path = Path(path).resolve()
    if not file_path.exists():
        raise ValueError(f"File {file_path} does not exist.")

    if file_path.is_dir():
        file_path = file_path / '__init__.py'

    file_extension = PurePath(file_path).suffix
    if file_extension != '.py':
        raise ValueError(f"Not a Python file {file_path} with extension '{file_extension}'.")

    return file_path


def get_module_parents(full_module_name: str) -> List[str]:
    """
    Returns a list module's parent packages and subpackages.
    Example: package1.subpackage1.module1 -> [package1, package1.subpackage1]
    """
    parts = full_module_name.split('.')
    parts.pop()
    parents = []
    while parts:
        parents.insert(0, '.'.join(parts))
        parts.pop()
    return parents


def get_module_from_path(path: Union[Path, str], package_root: Union[Path, str]) -> str:
    """
    Converts the path within the package_root to a full module name starting with the package.
    """
    path = Path(path).resolve()
    root = Path(package_root).resolve()
    parts = list(path.parent.relative_to(root.parent).parts)
    if path.stem != '__init__':
        parts.append(path.stem)
    module = '.'.join(parts)
    return module
