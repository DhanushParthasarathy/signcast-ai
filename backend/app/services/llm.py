import asyncio
import json
import re
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any, Protocol

from openai import APIConnectionError, APIStatusError, APITimeoutError, AsyncOpenAI, RateLimitError

from app.core.config import Settings
from app.services.prompts import DEFAULT_SUMMARIZER_PROMPT_VERSION, PromptTemplate, get_prompt
from app.services.text_utils import extract_summary, simplify_english, split_sentences


MODEL_PRICING_USD_PER_1K_TOKENS: dict[str, tuple[float, float]] = {
    "gpt-4.1-mini": (0.0004, 0.0016),
    "gpt-4o-mini": (0.00015, 0.0006),
}


@dataclass(frozen=True)
class LLMUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0


@dataclass(frozen=True)
class LLMTextResult:
    headline: str
    summary: str
    simple_english: str
    model_name: str
    prompt_version: str = DEFAULT_SUMMARIZER_PROMPT_VERSION
    usage: LLMUsage = LLMUsage()


class LLMClient(Protocol):
    model_name: str

    async def summarize_for_accessibility(
        self,
        text: str,
        prompt_version: str | None = None,
    ) -> LLMTextResult:
        pass

    async def stream_summarize_for_accessibility(
        self,
        text: str,
        prompt_version: str | None = None,
    ) -> AsyncIterator[str]:
        yield ""


class CostTracker:
    def estimate(self, model_name: str, prompt_tokens: int, completion_tokens: int) -> LLMUsage:
        input_price, output_price = MODEL_PRICING_USD_PER_1K_TOKENS.get(model_name, (0.0, 0.0))
        cost = (prompt_tokens / 1000 * input_price) + (completion_tokens / 1000 * output_price)
        return LLMUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            estimated_cost_usd=round(cost, 8),
        )


class RuleBasedLLMClient:
    model_name = "rule-based-local"

    async def summarize_for_accessibility(
        self,
        text: str,
        prompt_version: str | None = None,
    ) -> LLMTextResult:
        prompt = get_prompt(prompt_version)
        headline = self._headline(text)
        summary = extract_summary(text)
        simple_english = normalize_sentence_limit(self._limit_sentences(simplify_english(summary), fallback=text))
        return LLMTextResult(
            headline=headline,
            summary=summary,
            simple_english=simple_english,
            model_name=self.model_name,
            prompt_version=prompt.version,
        )

    async def stream_summarize_for_accessibility(
        self,
        text: str,
        prompt_version: str | None = None,
    ) -> AsyncIterator[str]:
        result = await self.summarize_for_accessibility(text, prompt_version)
        payload = json.dumps(result_to_payload(result))
        for token in payload.split(" "):
            yield token + " "

    def _headline(self, text: str) -> str:
        first_sentence = split_sentences(text)[0] if split_sentences(text) else text
        words = re.sub(r"[^A-Za-z0-9' -]+", "", first_sentence).split()
        return " ".join(words[:12]) or "Untitled news story"

    def _limit_sentences(self, text: str, fallback: str) -> str:
        sentences = split_sentences(text)
        if len(sentences) >= 3:
            return " ".join(sentences[:5])
        fallback_sentences = split_sentences(simplify_english(fallback))
        combined = sentences + [item for item in fallback_sentences if item not in sentences]
        return " ".join(combined[:5]) if combined else text


class OpenAILLMClient:
    def __init__(
        self,
        api_key: str,
        model_name: str,
        *,
        max_retries: int = 3,
        retry_base_delay_seconds: float = 0.5,
        cost_tracker: CostTracker | None = None,
    ) -> None:
        self.model_name = model_name
        self.client = AsyncOpenAI(api_key=api_key)
        self.max_retries = max_retries
        self.retry_base_delay_seconds = retry_base_delay_seconds
        self.cost_tracker = cost_tracker or CostTracker()

    async def summarize_for_accessibility(
        self,
        text: str,
        prompt_version: str | None = None,
    ) -> LLMTextResult:
        prompt = get_prompt(prompt_version)

        async def request() -> Any:
            return await self.client.chat.completions.create(
                model=self.model_name,
                messages=self._messages(prompt, text),
                temperature=0.2,
                response_format={"type": "json_object"},
            )

        response = await self._with_retries(request)
        content = response.choices[0].message.content or "{}"
        payload = parse_summary_json(content)
        usage = getattr(response, "usage", None)
        tracked_usage = self.cost_tracker.estimate(
            self.model_name,
            prompt_tokens=getattr(usage, "prompt_tokens", 0) or 0,
            completion_tokens=getattr(usage, "completion_tokens", 0) or 0,
        )
        return LLMTextResult(
            headline=payload["headline"],
            summary=payload["summary"],
            simple_english=normalize_sentence_limit(payload["simple_english"]),
            model_name=self.model_name,
            prompt_version=prompt.version,
            usage=tracked_usage,
        )

    async def stream_summarize_for_accessibility(
        self,
        text: str,
        prompt_version: str | None = None,
    ) -> AsyncIterator[str]:
        prompt = get_prompt(prompt_version)

        async def request() -> Any:
            return await self.client.chat.completions.create(
                model=self.model_name,
                messages=self._messages(prompt, text),
                temperature=0.2,
                response_format={"type": "json_object"},
                stream=True,
            )

        stream = await self._with_retries(request)
        async for chunk in stream:
            choice = chunk.choices[0] if chunk.choices else None
            delta = getattr(choice, "delta", None) if choice else None
            content = getattr(delta, "content", None)
            if content:
                yield content

    async def _with_retries(self, operation: Any) -> Any:
        retryable = (APIConnectionError, APITimeoutError, RateLimitError, APIStatusError)
        last_error: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                return await operation()
            except retryable as exc:
                last_error = exc
                if (
                    isinstance(exc, APIStatusError)
                    and not isinstance(exc, RateLimitError)
                    and exc.status_code < 500
                ):
                    raise
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(self.retry_base_delay_seconds * (2**attempt))
        raise RuntimeError("LLM request failed") from last_error

    def _messages(self, prompt: PromptTemplate, text: str) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": prompt.system},
            {"role": "user", "content": prompt.render_user(text)},
        ]


def parse_summary_json(content: str) -> dict[str, str]:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        parsed = {}
    return {
        "headline": str(parsed.get("headline") or "Untitled news story").strip(),
        "summary": str(parsed.get("summary") or "").strip(),
        "simple_english": str(parsed.get("simple_english") or parsed.get("summary") or "").strip(),
    }


def normalize_sentence_limit(text: str) -> str:
    sentences = split_sentences(simplify_english(text))
    if not sentences:
        return simplify_english(text)
    if len(sentences) < 3:
        sentences.extend(
            [
                "The article explains the main event.",
                "It uses simpler words for easier reading.",
                "The key details are kept short.",
            ][: 3 - len(sentences)]
        )
    return " ".join(sentences[:5])


def result_to_payload(result: LLMTextResult) -> dict[str, str]:
    return {
        "headline": result.headline,
        "summary": result.summary,
        "simple_english": result.simple_english,
    }


def build_llm_client(settings: Settings) -> LLMClient:
    if settings.llm_provider == "openai" and settings.openai_api_key:
        return OpenAILLMClient(
            settings.openai_api_key,
            settings.llm_model,
            max_retries=settings.llm_max_retries,
            retry_base_delay_seconds=settings.llm_retry_base_delay_seconds,
        )
    return RuleBasedLLMClient()
