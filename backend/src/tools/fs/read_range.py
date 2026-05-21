from pathlib import Path
from src.tools.decorator import tool


@tool
def read_range(path: str, start: int, end: int):
    """
    Read specific lines from file

    path: file path
    start: start line
    end: end line
    """

    lines = Path(path).read_text(encoding="utf-8").splitlines()

    start = max(1, start)
    end = min(len(lines), end)

    result = []

    for i in range(start - 1, end):
        result.append(f"{i + 1:4} | {lines[i]}")

    return "\n".join(result)
