from collections.abc import AsyncIterator

from pydantic import BaseModel, Field

from app.services.llm import LLMClient, LLMUsage, result_to_payload
from app.services.prompts import DEFAULT_SUMMARIZER_PROMPT_VERSION


class ArticleSummary(BaseModel):
    headline: str
    summary: str
    simple_english: str
    prompt_version: str = DEFAULT_SUMMARIZER_PROMPT_VERSION
    model_name: str
    usage: LLMUsage = Field(default_factory=LLMUsage)


class SummarizerService:
    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    async def summarize_article(
        self,
        article: str,
        prompt_version: str | None = None,
    ) -> ArticleSummary:
        result = await self.llm_client.summarize_for_accessibility(article, prompt_version)
        return ArticleSummary(
            headline=result.headline,
            summary=result.summary,
            simple_english=result.simple_english,
            prompt_version=result.prompt_version,
            model_name=result.model_name,
            usage=result.usage,
        )

    async def stream_article_summary(
        self,
        article: str,
        prompt_version: str | None = None,
    ) -> AsyncIterator[str]:
        async for chunk in self.llm_client.stream_summarize_for_accessibility(article, prompt_version):
            yield chunk

    async def summarize_article_payload(
        self,
        article: str,
        prompt_version: str | None = None,
    ) -> dict[str, str]:
        result = await self.llm_client.summarize_for_accessibility(article, prompt_version)
        return result_to_payload(result)
