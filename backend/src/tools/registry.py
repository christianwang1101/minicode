class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, name, description, schema, func):
        print(f"[REGISTER TOOL] {name}")
        self.tools[name] = {
            "name": name,
            "description": description,
            "parameters": schema,
            "func": func,
        }

    def get(self, name):
        return self.tools[name]

    def schemas(self):
        tools = []

        for t in self.tools.values():
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t["description"],
                        "parameters": t["parameters"],
                    },
                }
            )

        return tools


_registry = ToolRegistry()

def register_tool(name, description, schema, func):
    _registry.register(name, description, schema, func)

def get_registry():
    return _registry
