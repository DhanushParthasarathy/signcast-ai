import pytest

from app.core.config import Settings
from app.services.ai_pipeline import AIPipelineService


@pytest.mark.asyncio
async def test_translate_to_gloss_removes_filler_words() -> None:
    service = AIPipelineService(Settings())

    gloss, tokens = await service.translate_to_gloss(
        "NASA launched a new satellite. It will watch Earth's climate."
    )

    assert gloss == "NASA LAUNCH SATELLITE WATCH EARTH CLIMATE"
    assert tokens == ["NASA", "LAUNCH", "SATELLITE", "WATCH", "EARTH", "CLIMATE"]
