from typing import Optional, Dict, Any

from src.core.agent import Agent
from src.plan.planner import PlanGenerator
from src.plan.builder import Builder


class Controller:
    def __init__(self, agent: Agent, planner: PlanGenerator, builder: Builder):
        self.agent = agent
        self.planner = planner
        self.builder = builder

    def chat_stream(self, user_input: str, mode: str = "build"):
        # 前端 mode 优先于自动判断
        if mode == "plan":
            yield from self.agent.chat_stream(user_input, mode)
            return

        # 只有 build 模式才自动判断
        if not self._should_plan(user_input):
            yield from self.agent.chat_stream(user_input, mode)
            return

        # plan 生成要"可见"
        yield {"type": "thinking", "content": "Planning..."}

        plan = self.planner.generate_plan(user_input)

        # 空计划 fallback
        if not plan.steps:
            yield from self.agent.chat_stream(user_input, mode)
            return

        # 根据 builder mode 决定行为
        if self.builder.mode == "plan":
            yield {"type": "plan", "content": plan.to_dict()}
            yield {"type": "message_end"}
            return

        # build 模式：一步一步执行
        if self.builder.mode == "build":
            self.builder.set_plan(plan)

            # 防无限空转
            max_steps = 10
            count = 0

            while not plan.is_complete():
                count += 1
                if count > max_steps:
                    yield {"type": "error", "content": "Plan execution limit reached"}
                    break

                result = self.builder.execute_next()

                # 流式体验 + error 分流
                yield {"type": "thinking", "content": f"Step {result.get('step')}..."}

                status = result.get("status")
                if status == "error":
                    yield {"type": "error", "content": result}
                else:
                    yield {"type": "plan_step", "content": result}

            yield {"type": "message_end"}
            return

        # fallback：完全走原 Agent
        yield from self.agent.chat_stream(user_input, mode)

    def _should_plan(self, text: str) -> bool:
        keywords = ["步骤", "step", "先", "然后", "执行", "读取", "分析", "帮我", "请"]
        return any(k in text for k in keywords)
