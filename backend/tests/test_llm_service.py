import pytest

from app.core.config import Settings
from app.services import llm as llm_module
from app.services.llm import CostTracker, OpenAILLMClient, RuleBasedLLMClient, build_llm_client
from app.services.prompts import DEFAULT_SUMMARIZER_PROMPT_VERSION, get_prompt
from app.services.summarizer import SummarizerService


@pytest.mark.asyncio
async def test_rule_based_summarizer_returns_required_payload() -> None:
    service = SummarizerService(RuleBasedLLMClient())

    result = await service.summarize_article(
        "NASA launched a climate satellite. The satellite will watch Earth. "
        "Scientists will use the data to study storms and heat."
    )

    assert result.headline
    assert result.summary
    assert result.simple_english
    assert 3 <= len([part for part in result.simple_english.split(".") if part.strip()]) <= 5
    assert result.prompt_version == DEFAULT_SUMMARIZER_PROMPT_VERSION


def test_prompt_versioning_returns_known_prompt() -> None:
    prompt = get_prompt("summarizer.v1")

    assert prompt.version == "summarizer.v1"
    assert "headline" in prompt.system


def test_cost_tracker_estimates_known_model_cost() -> None:
    usage = CostTracker().estimate("gpt-4.1-mini", prompt_tokens=1000, completion_tokens=500)

    assert usage.total_tokens == 1500
    assert usage.estimated_cost_usd == 0.0012


def test_build_llm_client_uses_rule_based_fallback_without_api_key() -> None:
    client = build_llm_client(Settings(llm_provider="openai", openai_api_key=""))

    assert isinstance(client, RuleBasedLLMClient)


@pytest.mark.asyncio
async def test_retry_logic_retries_transient_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    async def no_sleep(_: float) -> None:
        return None

    monkeypatch.setattr(llm_module.asyncio, "sleep", no_sleep)
    monkeypatch.setattr(llm_module, "APITimeoutError", RuntimeError)
    monkeypatch.setattr(llm_module, "APIConnectionError", ConnectionError)
    monkeypatch.setattr(llm_module, "RateLimitError", TimeoutError)
    monkeypatch.setattr(llm_module, "APIStatusError", ValueError)

    client = object.__new__(OpenAILLMClient)
    client.max_retries = 3
    client.retry_base_delay_seconds = 0
    attempts = 0

    async def flaky_operation() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise RuntimeError("temporary timeout")
        return "ok"

    result = await client._with_retries(flaky_operation)

    assert result == "ok"
    assert attempts == 3
