import shutil
from minicode.tools.decorator import tool


@tool
def move_file(src: str, dst: str):
    """
    Move or rename a file

    src: source path
    dst: destination path
    """

    shutil.move(src, dst)

    return f"moved {src} -> {dst}"
