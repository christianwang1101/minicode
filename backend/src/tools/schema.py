import inspect
from typing import get_origin, get_args, Union, Literal

from .docstring import parse_docstring


def python_type_to_json(t):

    mapping = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
    }

    return mapping.get(t, "string")


def resolve_type(annotation):

    origin = get_origin(annotation)

    if origin is list:
        item = get_args(annotation)[0]

        return {"type": "array", "items": {"type": python_type_to_json(item)}}

    if origin is Union:
        args = get_args(annotation)

        non_none = [a for a in args if a is not type(None)]

        if non_none:
            return {"type": python_type_to_json(non_none[0])}

    if origin is Literal:
        values = get_args(annotation)

        return {"type": "string", "enum": list(values)}

    return {"type": python_type_to_json(annotation)}


def build_tool(func):

    sig = inspect.signature(func)

    description, param_docs = parse_docstring(func)

    properties = {}
    required = []

    for name, param in sig.parameters.items():
        if param.annotation == inspect._empty:
            schema = {"type": "string"}

        else:
            schema = resolve_type(param.annotation)

        if name in param_docs:
            schema["description"] = param_docs[name]

        properties[name] = schema

        if param.default == inspect._empty:
            required.append(name)

    parameters = {"type": "object", "properties": properties, "required": required}

    return {"name": func.__name__, "description": description, "parameters": parameters}
