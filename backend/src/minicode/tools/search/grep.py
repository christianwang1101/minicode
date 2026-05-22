from pathlib import Path
from minicode.tools.decorator import tool


@tool
def grep(pattern: str, path: str = "."):
    """
    Search text inside files

    pattern: search text
    path: search directory
    """

    results = []

    for file in Path(path).rglob("*.py"):
        try:
            lines = file.read_text(encoding="utf-8").splitlines()

            for i, line in enumerate(lines):
                if pattern in line:
                    results.append(f"{file}:{i + 1}: {line.strip()}")

        except:
            pass

    return "\n".join(results) if results else "no match"
