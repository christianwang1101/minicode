from src.tools.decorator import tool


@tool
def append_file(path: str, content: str):
    """
    Append content to a file

    path: file path
    content: text to append
    """

    with open(path, "a", encoding="utf-8") as f:
        f.write(content)

    return "content appended"
