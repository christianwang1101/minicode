from pathlib import Path
from src.tools.decorator import tool


@tool
def replace_in_file(path: str, old: str, new: str):
    """
    Replace text inside a file

    path: file path
    old: text to replace
    new: replacement text
    """

    p = Path(path)

    if not p.exists():
        return f"{path} not found"

    text = p.read_text(encoding="utf-8")

    if old not in text:
        return "text not found"

    text = text.replace(old, new)

    p.write_text(text, encoding="utf-8")

    return "replacement done"
