from pathlib import Path
from src.tools.decorator import tool


@tool
def make_dir(path: str):
    """
    Create a directory

    path: directory path
    """

    Path(path).mkdir(parents=True, exist_ok=True)

    return f"directory created: {path}"
