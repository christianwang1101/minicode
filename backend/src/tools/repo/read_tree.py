from pathlib import Path
from src.tools.decorator import tool
from src.tools.ignore import should_ignore


@tool
def read_tree(path: str):
    """
    Read project directory tree

    Args:
        path: project root path
    """

    root = Path(path)

    if not root.exists():
        return "路径不存在"

    if not root.is_dir():
        return "路径不是文件夹"

    lines = []
    lines.append(f"{root.name}/")

    def get_children(current: Path):
        """✅ 使用统一 ignore 策略"""
        try:
            children = list(current.iterdir())
        except PermissionError:
            return []

        # ✅ 核心：统一过滤
        filtered = [c for c in children if not should_ignore(c)]

        return sorted(filtered, key=lambda x: x.name)

    def traverse(current: Path, prefix: str = ""):
        children = get_children(current)
        total = len(children)

        for i, child in enumerate(children):
            is_last = i == total - 1
            connector = "└── " if is_last else "├── "

            lines.append(
                f"{prefix}{connector}{child.name}{'/' if child.is_dir() else ''}"
            )

            if child.is_dir():
                new_prefix = prefix + ("    " if is_last else "│   ")
                traverse(child, new_prefix)

    traverse(root)

    return "\n".join(lines)
