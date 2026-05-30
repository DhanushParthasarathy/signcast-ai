from app.core.config import Settings
from app.services.gloss import ASLGlossService
from app.services.llm import build_llm_client


class AIPipelineService:
    def __init__(self, settings: Settings) -> None:
        self.llm = build_llm_client(settings)
        self.gloss = ASLGlossService()

    async def summarize(self, text: str) -> tuple[str, str]:
        result = await self.llm.summarize_for_accessibility(text)
        return result.summary, result.simple_english

    async def translate_to_gloss(self, text: str) -> tuple[str, list[str]]:
        return self.gloss.generate(text)
