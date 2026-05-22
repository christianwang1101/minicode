import ast
from pathlib import Path
from minicode.tools.decorator import tool


IGNORE_DIRS = {".git", "__pycache__", ".venv", "node_modules"}


@tool
def search_symbol(query: str, path: str = "."):
    """
    Search for class or function definitions

    query: symbol name
    path: search directory
    """

    root = Path(path).resolve()

    results = []

    for file in root.rglob("*.py"):
        if any(p in IGNORE_DIRS for p in file.parts):
            continue

        try:
            source = file.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except Exception:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if query.lower() in node.name.lower():
                    results.append(f"{file}:{node.lineno} class {node.name}")

            elif isinstance(node, ast.FunctionDef):
                if query.lower() in node.name.lower():
                    results.append(f"{file}:{node.lineno} def {node.name}")

    if not results:
        return "No symbol found"

    return "\n".join(results[:50])
