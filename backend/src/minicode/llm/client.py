from minicode.llm.providers.qwen import QwenProvider
from minicode.llm.providers.glm import GLMProvider
from minicode.llm.router import ModelRouter
from minicode.memory.context import Messages

class ModelClient:
    def __init__(self, router: ModelRouter):
        self.router = router

    def chat_stream(self, messages: Messages, tools=None):
        return self._generate_stream(messages, tools)

    def _generate_stream(self, messages: Messages, tools=None):
        provider: QwenProvider | GLMProvider = self.router.get_primary()
        print(f"[ModelClient] Using provider: {provider}")

        try:
            yield from provider.generate_stream(messages, tools)
        except Exception as e:
            print(f"[ModelClient] Primary provider error: {e}")
            try:
                provider = self.router.get_fallback()
                print(f"[ModelClient] Falling back to: {provider}")
                yield from provider.generate_stream(messages, tools)
            except Exception as e2:
                print(f"[ModelClient] Fallback also failed: {e2}")
                yield {"type": "error", "content": f"LLM Error: {e2}"}
