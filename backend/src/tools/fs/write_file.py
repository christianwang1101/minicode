from src.tools.decorator import tool


@tool
def write_file(path: str, content: str):
    """
    Write content to file

    path: file path
    content: text to write
    """

    with open(path, "w") as f:
        f.write(content)

    return "ok"
