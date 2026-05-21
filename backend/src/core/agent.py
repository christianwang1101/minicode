import json
from typing import List, Dict, Any
from src.llm.client import ModelClient
from src.memory.context import Context
from src.memory.context import Messages
from src.runtime.step_controller import StepController
from src.tools.registry import ToolRegistry
from src.tools.runner import ToolRunner
from src import config


class Agent:
    def __init__(
        self,
        llm: ModelClient,
        memory: Context,
        registry: ToolRegistry,
        runner: ToolRunner,
        step_controller: StepController,
    ):
        self.llm = llm
        self.memory = memory
        self.registry = registry
        self.runner = runner
        self.step_controller = step_controller

    def chat_stream(self, user_input: str, mode: str = "build"):
        self.step_controller.reset()
        self.memory.add("user", user_input)

        while True:
            if not self.step_controller.next():
                yield {"type": "thinking", "content": "[STOP] step limit reached"}
                yield {"type": "message_end"}
                return

            messages: Messages = self.memory.get()
            tools = self.registry.schemas() or []

            # 根据 mode 过滤工具
            if mode == "plan":
                safe_tools = config.SAFE_TOOLS
                tools = [t for t in tools if t["function"]["name"] in safe_tools]

            response = self.llm.chat_stream(messages=messages, tools=tools)

            tool_call = None
            text_parts = []

            for chunk in response:
                t = chunk.get("type")

                if t == "text":
                    token = chunk.get("content", "")
                    text_parts.append(token)
                    yield {"type": "token", "content": token}

                elif t == "tool_call" and tool_call is None:
                    tool_call = chunk

            full_text = "".join(text_parts)
            if full_text:
                self.memory.add("assistant", full_text)

            if tool_call:
                name = tool_call.get("name", "")
                args = tool_call.get("arguments", {})

                if not name:
                    yield {
                        "type": "tool_result",
                        "name": "",
                        "content": "Error: empty tool name",
                    }
                    continue

                if name not in self.registry.tools:
                    yield {
                        "type": "tool_result",
                        "name": name,
                        "content": f"Error: unknown tool '{name}'",
                    }
                    continue

                if not isinstance(args, dict):
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except:
                            yield {
                                "type": "tool_result",
                                "name": name,
                                "content": "Error: invalid arguments format",
                            }
                            continue
                    else:
                        yield {
                            "type": "tool_result",
                            "name": name,
                            "content": "Error: invalid arguments format",
                        }
                        continue

                yield {"type": "thinking", "content": f"Calling tool: {name}"}
                yield {"type": "tool_call", "name": name, "args": args}

                result = self.runner.run(name, args)

                yield {"type": "thinking", "content": "Processing result..."}
                yield {"type": "tool_result", "name": name, "content": result}

                call_id = tool_call.get("id") or "tool_0"

                self.memory.add_raw(
                    {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": call_id,
                                "type": "function",
                                "function": {
                                    "name": name,
                                    "arguments": json.dumps(args, ensure_ascii=False),
                                },
                            }
                        ],
                    }
                )

                self.memory.add_raw(
                    {"role": "tool", "tool_call_id": call_id, "content": str(result)}
                )

                continue

            else:
                yield {"type": "message_end"}
                return
