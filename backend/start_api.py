from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src import config
from src.core.agent import Agent
from src.core.controller import Controller
from src.llm.client import ModelClient
from src.llm.providers.glm import GLMProvider
from src.llm.providers.qwen import QwenProvider
from src.llm.router import ModelRouter
from src.memory.context import Context
from src.plan.planner import PlanGenerator
from src.plan.builder import Builder
from src.runtime.step_controller import StepController
from src.tools.loader import load_tools
from src.tools.registry import get_registry
from src.tools.runner import ToolRunner
import json


def _create_controller():
    load_tools()

    memory = Context()
    registry = get_registry()
    runner = ToolRunner(registry)
    step_controller = StepController(config.MAX_STEP)

    providers: dict[str, QwenProvider | GLMProvider] = {
        "qwen": QwenProvider(
            api_key=config.QWEN_API_KEY,
            model=config.QWEN_MODEL,
            endpoint=config.QWEN_ENDPOINT,
        ),
        "glm": GLMProvider(
            api_key=config.GLM_API_KEY,
            model=config.GLM_MODEL,
            endpoint=config.GLM_ENDPOINT,
        ),
    }

    router = ModelRouter(
        providers=providers,
        primary=config.PRIMARY_PROVIDER,
        fallback=config.FALLBACK_PROVIDER,
    )

    llm = ModelClient(router)

    agent = Agent(
        llm=llm,
        memory=memory,
        registry=registry,
        runner=runner,
        step_controller=step_controller,
    )

    planner = PlanGenerator(llm, registry)
    plan_builder = Builder(runner)

    controller = Controller(agent, planner, plan_builder)

    return controller


print(f"[DEBUG] QWEN_API_KEY: {config.QWEN_API_KEY[:10]}...")
print(f"[DEBUG] QWEN_ENDPOINT: {config.QWEN_ENDPOINT}")

app = FastAPI(title="MiniCode API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = _create_controller()


@app.get("/")
async def root():
    return {"message": "MiniCode API is running", "version": "1.0.0"}


@app.post("/chat")
async def chat(req: Request):
    data = await req.json()
    message = data.get("message", "")
    mode = data.get("mode", "build")
    # 防御性处理：校验 mode
    if mode not in ("build", "plan"):
        mode = "build"

    if not message.strip():
        return JSONResponse({"error": "Empty message"}, status_code=400)

    def event_stream():
        for event in agent.chat_stream(message, mode):
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/ping")
async def ping():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
