from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from minicode import config
from minicode.core.agent import Agent
from minicode.core.controller import Controller
from minicode.llm.client import ModelClient
from minicode.llm.providers.glm import GLMProvider
from minicode.llm.providers.qwen import QwenProvider
from minicode.llm.providers.deepseek import DeepSeekProvider
from minicode.llm.router import ModelRouter
from minicode.memory.context import Context
from minicode.plan.planner import PlanGenerator
from minicode.plan.builder import Builder
from minicode.runtime.step_controller import StepController
from minicode.tools.loader import load_tools
from minicode.tools.registry import get_registry
from minicode.tools.runner import ToolRunner
import json


def _create_controller():
    load_tools()

    memory = Context()
    registry = get_registry()
    runner = ToolRunner(registry)
    step_controller = StepController(config.MAX_STEP)

    providers: dict[str, QwenProvider | GLMProvider | DeepSeekProvider] = {
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
        "deepseek": DeepSeekProvider(
            api_key=config.DEEPSEEK_API_KEY,
            model=config.DEEPSEEK_MODEL,
            endpoint=config.DEEPSEEK_ENDPOINT,
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


def main():
    import subprocess
    import sys
    import os
    import signal
    import shutil

    frontend_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "frontend", "Vue")
    )

    frontend_proc = None
    npm_path = shutil.which("npm")
    if npm_path and os.path.isdir(os.path.join(frontend_dir, "node_modules")):
        frontend_proc = subprocess.Popen(
            [npm_path, "run", "dev"],
            cwd=frontend_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        print(f"[MiniCode] Frontend starting at http://localhost:5173")

        import threading
        def open_browser():
            import time, webbrowser
            time.sleep(3)
            webbrowser.open("http://localhost:5173")
        threading.Thread(target=open_browser, daemon=True).start()
    else:
        missing = []
        if not npm_path:
            missing.append("npm not found in PATH")
        if not os.path.isdir(os.path.join(frontend_dir, "node_modules")):
            missing.append("node_modules missing (run npm install)")
        print(f"[MiniCode] Frontend not started: {', '.join(missing)}")

    import uvicorn

    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
    finally:
        if frontend_proc:
            frontend_proc.terminate()
            frontend_proc.wait()


if __name__ == "__main__":
    main()
