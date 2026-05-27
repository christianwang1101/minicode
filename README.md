# Minicode

MiniCode is a minimal AI coding assistant with a Vue frontend, a FastAPI backend, and a tool-driven agent loop that can plan, inspect, and modify code. It is designed to be lightweight, local-first, and easy to extend with additional tools or model providers.

## Project Description

MiniCode combines three layers:

- a browser UI for chatting with the assistant and browsing the project tree
- a backend agent that streams responses and tool activity over Server-Sent Events
- a modular tool registry that loads file, repo, search, and system helpers at startup

The assistant can work in two modes:

- `build`: full agent mode with the complete tool set available
- `plan`: restricted mode that only exposes safe read-only tools

## Characteristics

- Minimal architecture with a clear separation between UI, API, agent, and tools
- Streaming chat responses for a responsive editing workflow
- Model routing with primary and fallback providers
- Extensible tool discovery through automatic package loading
- Explicit limits on tool loops and agent steps to reduce runaway behavior
- Built-in support for code reading, repo inspection, and filesystem operations

## Architecture And Workflow

The runtime starts in `backend/src/minicode/main.py`, which builds the controller stack in this order:

1. Load all tool modules from `minicode.tools`.
2. Create shared memory, tool registry, and tool runner instances.
3. Configure model providers for Qwen, GLM, and DeepSeek.
4. Route provider selection through `ModelRouter`.
5. Create the agent, planner, and builder.
6. Expose the FastAPI app with `/`, `/ping`, and `/chat` endpoints.

The request flow is:

1. The frontend sends a chat message to `/chat`.
2. The backend streams tokens, thinking events, tool calls, and tool results.
3. The agent stores conversation state in memory and may call tools.
4. The frontend renders the stream as it arrives.

In `plan` mode, the agent filters the available tools to the allowlist defined in `backend/src/minicode/config.py`.

## Prerequisites

- Python 3.10 or newer
- Node.js 20.19+ or 22.12+
- npm
- Access to at least one supported model provider

Optional but recommended environment variables for the backend:

- `QWEN_API_KEY`
- `QWEN_ENDPOINT`
- `QWEN_MODEL`
- `GLM_API_KEY`
- `GLM_ENDPOINT`
- `GLM_MODEL`
- `DEEPSEEK_API_KEY`
- `DEEPSEEK_ENDPOINT`
- `DEEPSEEK_MODEL`
- `PRIMARY_PROVIDER`
- `FALLBACK_PROVIDER`

## Installation Guide

### Backend

From the `backend` directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
uv sync
```

If you use a `.env` file, place it in `backend/.env`.

### Frontend

From `frontend/Vue`:

```bash
npm install
```

## Usage Guide

### Start The Backend

```bash
cd backend
source .venv/bin/activate
python start_api.py
```

The API listens on `http://127.0.0.1:8000`.

### Start The Frontend

```bash
cd frontend/Vue
npm run dev
```

The Vite dev server proxies `/chat` and `/ping` to the backend on port `8000`.

### One-Click Launch (Recommended)

After installing the backend (see below), run from any path:

```bash
minicode
```

This starts both the backend and frontend simultaneously and opens the browser automatically. Press `Ctrl+C` to stop both.

### One-Click Launch On macOS (Legacy)

The root `start_api.sh` script opens separate Terminal windows for the frontend and backend. It uses `osascript`, so it is macOS-specific.

### API Endpoints

- `GET /` returns a basic health message
- `GET /ping` returns `{"status":"ok"}`
- `POST /chat` accepts `{ "message": "...", "mode": "build|plan" }` and streams SSE events

## Agent Configurations

The backend agent is configured in `backend/src/minicode/config.py` and `backend/src/minicode/main.py`.

- Provider list: `qwen`, `glm`, `deepseek`
- Provider routing: `PRIMARY_PROVIDER` and `FALLBACK_PROVIDER`
- Step limit: `MAX_STEP = 4`
- Tool loop limit: `MAX_TOOL_LOOP = 4`
- Memory limit: `MEMORY_LIMIT = 50`
- Memory file: `.memory.json`
- Plan-mode safe tools: read-only search and repo inspection helpers only

The tool system is loaded dynamically by walking `minicode.tools`, so adding a new tool module under that package is usually enough to make it available to the agent.

## Limitations

- The `start_api.sh` launcher script is macOS-only because it depends on `osascript`. The `minicode` CLI works on any platform.
- The agent depends on external LLM endpoints and valid API credentials.
- `plan` mode intentionally disables write-capable tools.
- Conversation state is in-memory and limited by the configured memory cap.
- Agent behavior is bounded by fixed step and tool-loop limits, so very long or multi-stage tasks may be truncated.
- The frontend expects the backend to be running locally on port `8000`.

## Repository Layout

```text
backend/
	src/minicode/
		main.py      # API entry point and FastAPI app
		config.py    # environment config and agent limits
		core/        # agent and controller orchestration
		llm/         # providers, router, and client wrappers
		memory/      # conversation context management
		plan/        # planning and builder logic
		runtime/     # step controller and execution guards
		tools/       # tool registry, schemas, and implementations
frontend/Vue/
	src/          # Vue app, chat UI, editor, sidebar, and API client
```