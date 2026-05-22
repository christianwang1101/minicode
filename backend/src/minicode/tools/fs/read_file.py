from pathlib import Path
from minicode.tools.decorator import tool


@tool
def read_file(path: str):
    """
    Read a file

    path: file path
    """

    return Path(path).read_text(encoding="utf-8")
