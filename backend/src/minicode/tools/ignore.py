from pathlib import Path

IGNORE_DIRS = {"node_modules", "vue_minicode"}
IGNORE_PREFIXES = (".", "__")  # 以 . 或 __ 开头全部忽略


def should_ignore(path: Path) -> bool:
    name = path.name

    if name.startswith(IGNORE_PREFIXES):
        return True

    if path.is_dir() and name in IGNORE_DIRS:
        return True

    return False
