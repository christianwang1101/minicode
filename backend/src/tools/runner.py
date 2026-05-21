import json


class ToolRunner:
    def __init__(self, registry):
        self.registry = registry

    def run(self, name: str, args):

        tool = self.registry.get(name)

        func = tool["func"]

        try:
            # LLM 可能返回 JSON string
            if isinstance(args, str):
                args = json.loads(args)

            if args is None:
                args = {}

            result = func(**args)

            if result is None:
                result = "ok"

            return str(result)

        except Exception as e:
            return f"tool error: {str(e)}"
