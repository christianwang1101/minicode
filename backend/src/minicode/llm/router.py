from src import config
from src.llm.providers.qwen import QwenProvider
from src.llm.providers.glm import GLMProvider


class ModelRouter:
    def __init__(
        self,
        providers: dict[str, QwenProvider | GLMProvider],
        primary=config.PRIMARY_PROVIDER,
        fallback=config.FALLBACK_PROVIDER,
    ):
        self.providers = providers
        self.primary = primary
        self.fallback = fallback

    def get_primary(self) -> QwenProvider | GLMProvider:
        return self.providers[self.primary]

    def get_fallback(self) -> QwenProvider | GLMProvider:
        return self.providers[self.fallback]
