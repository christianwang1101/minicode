from .schema import build_tool
from .registry import register_tool


def tool(func):

    tool_def = build_tool(func)

    register_tool(
        name=tool_def["name"],
        description=tool_def["description"],
        schema=tool_def["parameters"],
        func=func,
    )

    return func
