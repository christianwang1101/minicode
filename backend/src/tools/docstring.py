import inspect


def parse_docstring(func):
    """
    Parse function docstring.

    Returns:
        description: first line summary
        params: dict of parameter descriptions
    """

    doc = inspect.getdoc(func)

    if not doc:
        return "", {}

    lines = doc.splitlines()

    description = lines[0].strip()

    params = {}

    in_args = False

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if line.lower().startswith("args"):
            in_args = True
            continue

        if in_args:
            if ":" in line:
                name, desc = line.split(":", 1)

                name = name.strip()
                desc = desc.strip()

                params[name] = desc

            else:
                # 遇到非参数行结束 Args 区域
                in_args = False

    return description, params
