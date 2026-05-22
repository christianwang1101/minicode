from pathlib import Path
import difflib
from minicode.tools.decorator import tool


@tool
def patch_file(path: str, new_content: str):
    """
    Patch file content and return diff

    path: file path
    new_content: new file content
    """

    p = Path(path)

    if not p.exists():
        old = ""
    else:
        old = p.read_text(encoding="utf-8")

    diff = difflib.unified_diff(old.splitlines(), new_content.splitlines(), lineterm="")

    patch = "\n".join(diff)

    p.write_text(new_content, encoding="utf-8")

    return patch if patch else "no changes"
