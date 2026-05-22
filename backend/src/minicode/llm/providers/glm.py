import requests
import json
from minicode import config
from minicode.memory.context import Messages


class GLMProvider:
    def __init__(
        self,
        api_key: str = config.GLM_API_KEY,
        model: str = config.GLM_MODEL,
        endpoint: str = config.GLM_ENDPOINT,
        timeout: int = 60,
    ):
        self.api_key = api_key
        self.model = model
        self.endpoint = endpoint
        self.timeout = timeout

    def generate_stream(self, messages: Messages, tools=None):
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

        tool_buffer = {}

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
            except:
                continue

            choices = data.get("choices", [])
            if not choices:
                continue

            delta = choices[0].get("delta", {})

            if "content" in delta and delta["content"]:
                yield {"type": "text", "content": delta["content"]}

            if "tool_calls" in delta:
                for index, func in enumerate(delta["tool_calls"]):
                    if index > 0:
                        break

                    call_id = f"tool_{index}"
                    if call_id not in tool_buffer:
                        tool_buffer[call_id] = {"name": "", "arguments": ""}
                    if func.get("name"):
                        tool_buffer[call_id]["name"] = func["name"]
                    if func.get("arguments"):
                        tool_buffer[call_id]["arguments"] += func["arguments"]

        for call_id, data in tool_buffer.items():
            name = data["name"]
            args_str = data["arguments"]

            if name and args_str:
                try:
                    args = json.loads(args_str)
                    yield {
                        "type": "tool_call",
                        "id": call_id,
                        "name": name,
                        "arguments": args,
                    }
                except Exception:
                    pass
