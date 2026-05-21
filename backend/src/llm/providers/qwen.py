import requests
import json
from src import config


class QwenProvider:
    def __init__(
        self,
        api_key: str = config.QWEN_API_KEY,
        model: str = config.QWEN_MODEL,
        endpoint: str = config.QWEN_ENDPOINT,
        timeout: int = 60,
    ):
        self.api_key = api_key
        self.model = model
        self.endpoint = endpoint
        self.timeout = timeout

    def generate_stream(self, messages, tools=None):
        """
        Streaming generator
        yield token or tool_call
        """
        tool_buffer: dict = {}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }

        if tools:
            payload["tools"] = tools

        resp = requests.post(
            self.endpoint,
            headers=headers,
            json=payload,
            stream=True,
            timeout=self.timeout,
        )

        resp.raise_for_status()

        for line in resp.iter_lines():
            if not line:
                continue

            line = line.decode("utf-8")

            if not line.startswith("data:"):
                continue

            data_str = line[5:].strip()

            if data_str == "[DONE]":
                break

            try:
                data = json.loads(data_str)

                delta = data["choices"][0]["delta"]

                if "content" in delta and delta["content"]:
                    yield {"type": "text", "content": delta["content"]}

                if "tool_calls" in delta:
                    for index, tool_call in enumerate(delta["tool_calls"]):
                        if index > 0:
                            break

                        call_id = f"tool_{index}"
                        func = tool_call.get("function", {})

                        if call_id not in tool_buffer:
                            tool_buffer[call_id] = {"name": "", "arguments": ""}

                        if "name" in func and func["name"]:
                            tool_buffer[call_id]["name"] = func["name"]

                        if "arguments" in func and func["arguments"]:
                            tool_buffer[call_id]["arguments"] += func["arguments"]

                        name = tool_buffer[call_id]["name"]
                        args = tool_buffer[call_id]["arguments"]

                        if name and args:
                            try:
                                parsed_args = json.loads(args)
                                result = {
                                    "type": "tool_call",
                                    "id": call_id,
                                    "name": name,
                                    "arguments": parsed_args,
                                }
                                yield result
                                del tool_buffer[call_id]
                            except json.JSONDecodeError:
                                pass

            except Exception:
                continue
