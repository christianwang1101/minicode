from pathlib import Path
from minicode.tools.decorator import tool


@tool
def list_dir(path: str = "."):
    """
    List files in a directory

    path: directory path
    """

    p = Path(path)

    files = []

    for item in p.iterdir():
        if item.is_dir():
            files.append(f"[DIR] {item.name}")
        else:
            files.append(item.name)

    return "\n".join(files)
