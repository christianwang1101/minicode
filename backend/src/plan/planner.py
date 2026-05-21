import json
import re
from typing import List, Dict, Any
from src.plan.schema import Plan, PlanStep, StepStatus
from src.llm.client import ModelClient


class PlanGenerator:
    def __init__(self, llm: ModelClient, registry):
        self.llm = llm
        self.registry = registry

    def generate_plan(self, message: str) -> Plan:
        system_prompt = """你是任务规划器。只允许返回 JSON 数组，不要解释，不要多余文字。

格式：[{"tool": "xxx", "arguments": {...}}]

可用的工具：read_file, write_file, list_dir, read_tree, grep, search_file, shell_run"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ]

        response = self.llm.chat_stream(messages=messages, tools=None)

        text = ""
        for chunk in response:
            if chunk.get("type") == "text":
                text += chunk.get("content", "")

        steps_data = self._parse(text)

        # 8. 工具白名单过滤
        valid_tools = set(self.registry.tools.keys())
        filtered = []
        for s in steps_data:
            tool = s.get("tool", "")
            if tool in valid_tools:
                filtered.append(s)

        # 3. 空计划 fallback
        if not filtered:
            return Plan([])

        steps = []
        for i, s in enumerate(filtered):
            steps.append(
                PlanStep(
                    step=i + 1,
                    tool=s.get("tool", ""),
                    arguments=s.get("arguments", {}),
                    status=StepStatus.PENDING,
                )
            )

        return Plan(steps)

    def _extract_json(self, text: str) -> str:
        match = re.search(r"\[.*\]", text, re.S)
        if match:
            return match.group(0)
        return "[]"

    def _parse(self, text: str) -> List[Dict[str, Any]]:
        try:
            json_str = self._extract_json(text)
            data = json.loads(json_str)
            if isinstance(data, list):
                return data
        except Exception:
            pass
        return []
