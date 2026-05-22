import os
from dotenv import load_dotenv

load_dotenv()

__all__ = [
    "QWEN_ENDPOINT",
    "QWEN_API_KEY",
    "QWEN_MODEL",
    "GLM_ENDPOINT",
    "GLM_API_KEY",
    "GLM_MODEL",
    "PRIMARY_PROVIDER",
    "FALLBACK_PROVIDER",
    "PROVIDERS",
    "MAX_TOOL_LOOP",
    "MAX_STEP",
    "MEMORY_LIMIT",
    "MEMORY_FILE",
    "SAFE_TOOLS",
]

# =========================
# LLM Providers
# =========================
PROVIDERS = ["qwen", "glm"]


QWEN_ENDPOINT = os.getenv("QWEN_ENDPOINT", "")
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-plus")


GLM_ENDPOINT = os.getenv("GLM_ENDPOINT", "")
GLM_API_KEY = os.getenv("GLM_API_KEY", "")
GLM_MODEL = os.getenv("GLM_MODEL", "glm-4")


# =========================
# Router
# =========================

PRIMARY_PROVIDER = os.getenv("PRIMARY_PROVIDER", "qwen")
FALLBACK_PROVIDER = os.getenv("FALLBACK_PROVIDER", "glm")

# =========================
# Agent Limits
# =========================

MAX_TOOL_LOOP = 4
MAX_STEP = 4


# =========================
# Memory
# =========================

MEMORY_LIMIT = 50
MEMORY_FILE = ".memory.json"


# =========================
# Safe Tools (Plan Mode)
# =========================
SAFE_TOOLS = {
    "read_file",
    "read_range",
    "read_tree",
    "read_repo",
    "repo_map",
    "grep",
    "search_file",
    "search_symbol",
    "list_dir",
}
