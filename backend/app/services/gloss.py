from dataclasses import dataclass, field

from app.services.rules import GlossRuleSet
from app.services.tokenizer import EnglishTokenizer


@dataclass(frozen=True)
class GlossTranslationResult:
    gloss_tokens: list[str]
    confidence: float
    unknown_tokens: list[str] = field(default_factory=list)

    @property
    def gloss(self) -> str:
        return " ".join(self.gloss_tokens)


class ASLGlossService:
    def __init__(
        self,
        tokenizer: EnglishTokenizer | None = None,
        rules: GlossRuleSet | None = None,
    ) -> None:
        self.tokenizer = tokenizer or EnglishTokenizer()
        self.rules = rules or GlossRuleSet()

    def translate(self, text: str) -> GlossTranslationResult:
        source_tokens = self.tokenizer.tokenize(text)
        gloss_tokens: list[str] = []
        unknown_tokens: list[str] = []
        meaningful_count = 0

        for token in source_tokens:
            decision = self.rules.translate_token(token)
            if decision.gloss_tokens:
                meaningful_count += 1
                gloss_tokens.extend(decision.gloss_tokens)
                if not decision.known:
                    unknown_tokens.extend(decision.gloss_tokens)

        confidence = self._confidence(meaningful_count, unknown_tokens)
        return GlossTranslationResult(
            gloss_tokens=dedupe_adjacent(gloss_tokens),
            confidence=confidence,
            unknown_tokens=dedupe_preserve_order(unknown_tokens),
        )

    def generate(self, text: str) -> tuple[str, list[str]]:
        result = self.translate(text)
        return result.gloss, result.gloss_tokens

    def _confidence(self, meaningful_count: int, unknown_tokens: list[str]) -> float:
        if meaningful_count == 0:
            return 0.0
        known_count = max(meaningful_count - len(unknown_tokens), 0)
        return round(known_count / meaningful_count, 2)


def dedupe_adjacent(tokens: list[str]) -> list[str]:
    deduped: list[str] = []
    for token in tokens:
        if not deduped or deduped[-1] != token:
            deduped.append(token)
    return deduped


def dedupe_preserve_order(tokens: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for token in tokens:
        if token not in seen:
            ordered.append(token)
            seen.add(token)
    return ordered
