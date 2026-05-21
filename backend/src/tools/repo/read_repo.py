import os
from pathlib import Path
from src.tools.decorator import tool
from src.tools.ignore import should_ignore

TEXT_EXTENSIONS = {".py", ".md", ".txt", ".html", ".js", ".toml", ".ts", ".vue", ".rs"}

MAX_FILE_SIZE = 200_000  # 200 KB


@tool
def read_repo(path: str):
    """
    Export repository files into a single file

    Args:
        path: project root path
    """

    root = Path(path).resolve()

    if not root.exists():
        return "path not found"

    result = []

    for current_root, dirs, files in os.walk(root):
        current_path = Path(current_root)

        # ✅ 关键修复：目录过滤（必须用 should_ignore）
        dirs[:] = [d for d in dirs if not should_ignore(current_path / d)]

        for file in files:
            file_path = current_path / file

            # ✅ 文件也要过滤（你之前漏了！）
            if should_ignore(file_path):
                continue

            # 扩展名过滤
            if file_path.suffix not in TEXT_EXTENSIONS:
                continue

            try:
                # 大文件跳过
                if file_path.stat().st_size > MAX_FILE_SIZE:
                    result.append(f"# SKIPPED large file: {file_path}")
                    continue

                content = file_path.read_text(encoding="utf-8")

                result.append(
                    f"""# ================================
# FILE: {file_path}
# ================================

{content}
"""
                )

            except Exception as e:
                result.append(f"# ERROR reading {file_path}: {str(e)}")

    return "\n".join(result)
