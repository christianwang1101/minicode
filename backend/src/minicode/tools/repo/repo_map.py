import ast
from pathlib import Path
from minicode.tools.decorator import tool
from minicode.tools.ignore import should_ignore


def parse_file(file_path: Path):
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except Exception:
        return None

    imports = []
    classes = []
    functions = []

    for node in tree.body:
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.append(n.name)

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imports.append(module)

        elif isinstance(node, ast.ClassDef):
            methods = []

            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    args = [a.arg for a in item.args.args]
                    methods.append(f"{item.name}({', '.join(args)})")

            classes.append((node.name, methods))

        elif isinstance(node, ast.FunctionDef):
            args = [a.arg for a in node.args.args]
            functions.append(f"{node.name}({', '.join(args)})")

    return {"imports": imports, "classes": classes, "functions": functions}


@tool
def repo_map(path: str = "."):
    """
    Generate repository map including imports, classes, functions

    Args:
        path: repository path
    """

    root = Path(path).resolve()

    if not root.exists():
        return "path not found"

    lines = ["REPO MAP", "========", ""]

    count = 0
    MAX_FILES = 200  # 防止爆炸

    for file in sorted(root.rglob("*.py")):
        # ✅ 关键1：过滤文件本身
        if should_ignore(file):
            continue

        # ✅ 关键2：过滤父目录（非常关键！）
        if any(should_ignore(p) for p in file.parents):
            continue

        info = parse_file(file)

        if not info:
            continue

        lines.append(str(file))

        if info["imports"]:
            lines.append("")
            lines.append("imports:")

            for imp in info["imports"]:
                lines.append(f"  {imp}")

        for cls, methods in info["classes"]:
            lines.append("")
            lines.append(f"class {cls}")

            for m in methods:
                lines.append(f"  {m}")

        for func in info["functions"]:
            lines.append("")
            lines.append(f"function {func}")

        lines.append("")
        lines.append("")

        count += 1
        if count >= MAX_FILES:
            lines.append("# TRUNCATED: too many files")
            break

    return "\n".join(lines)
