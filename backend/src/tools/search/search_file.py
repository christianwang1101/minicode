from pathlib import Path
from src.tools.decorator import tool


@tool
def search_file(query: str, path: str = "."):
    """
    Search files by name

    query: file name keyword
    path: search directory
    """

    results = []

    for p in Path(path).rglob("*"):
        if query.lower() in p.name.lower():
            results.append(str(p))

    return "\n".join(results) if results else "no match"
