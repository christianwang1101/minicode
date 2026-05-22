from pathlib import Path
from minicode.tools.decorator import tool


@tool
def delete_file(path: str):
    """
    Delete a file

    path: file path
    """

    p = Path(path)

    if not p.exists():
        return f"{path} not found"

    p.unlink()

    return f"{path} deleted"
