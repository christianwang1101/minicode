from typing import List, Dict, Any, Optional
from enum import Enum


class StepStatus(Enum):
    PENDING = "pending"
    DONE = "done"
    FAILED = "failed"


class PlanStep:
    def __init__(
        self,
        step: int,
        tool: str,
        arguments: Dict[str, Any],
        status: StepStatus = StepStatus.PENDING,
        result: Optional[str] = None,
    ):
        self.step = step
        self.tool = tool
        self.arguments = arguments
        self.status = status
        self.result = result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "tool": self.tool,
            "arguments": self.arguments,
            "status": self.status.value,
            "result": self.result,
        }


class Plan:
    def __init__(self, steps: List[PlanStep]):
        self.steps = steps
        self.current_step = 0

    def next_step(self) -> Optional[PlanStep]:
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            self.current_step += 1
            return step
        return None

    def is_complete(self) -> bool:
        return self.current_step >= len(self.steps)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "steps": [s.to_dict() for s in self.steps],
            "current_step": self.current_step,
            "total_step": len(self.steps),
        }
