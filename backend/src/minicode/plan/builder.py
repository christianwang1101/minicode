from typing import Optional, Dict, Any

from src.plan.schema import Plan, StepStatus


class Builder:
    def __init__(self, tool_runner):
        self.runner = tool_runner
        self.current_plan: Optional[Plan] = None
        self.mode = "build"  # build / plan

    def switch_mode(self):
        self.mode = "plan" if self.mode == "build" else "build"
        return self.mode

    def set_plan(self, plan: Plan):
        self.current_plan = plan

    def execute_next(self) -> Dict[str, Any]:
        if not self.current_plan:
            return {"status": "error", "error": "no plan"}

        step = self.current_plan.next_step()
        if not step:
            return {"status": "done"}

        # 4. 空工具检查
        if not step.tool:
            step.status = StepStatus.FAILED
            return {"status": "error", "step": step.step, "error": "Empty tool"}

        # 工具存在性检查
        if step.tool not in self.runner.registry.tools:
            step.status = StepStatus.FAILED
            step.result = f"Unknown tool: {step.tool}"
            return {
                "status": "error",
                "step": step.step,
                "error": f"Unknown tool: {step.tool}",
            }

        try:
            result = self.runner.run(step.tool, step.arguments)

            step.status = StepStatus.DONE
            step.result = str(result)

            return {
                "status": "success",
                "step": step.step,
                "tool": step.tool,
                "args": step.arguments,
                "result": result,
            }

        except Exception as e:
            step.status = StepStatus.FAILED
            step.result = str(e)

            return {
                "status": "error",
                "step": step.step,
                "tool": step.tool,
                "error": str(e),
            }
