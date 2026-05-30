from dataclasses import dataclass


@dataclass(frozen=True)
class PromptTemplate:
    version: str
    system: str
    user_template: str

    def render_user(self, article: str) -> str:
        return self.user_template.format(article=article.strip())


SUMMARIZER_PROMPT_V1 = PromptTemplate(
    version="summarizer.v1",
    system=(
        "You are SignCast AI's accessibility news editor. Transform full news articles "
        "for Deaf and hard-of-hearing readers and sign-language learners. "
        "Keep facts accurate. Use plain language. Remove complex jargon, idioms, and "
        "unnecessary detail. The simple_english field must be 3 to 5 short sentences. "
        "Return valid JSON only with these exact keys: headline, summary, simple_english."
    ),
    user_template=(
        "Rewrite this full news article for accessibility.\n\n"
        "Rules:\n"
        "- headline: short factual headline, 12 words or fewer\n"
        "- summary: concise factual summary, 1 to 2 sentences\n"
        "- simple_english: 3 to 5 short plain-language sentences\n"
        "- remove complex jargon or explain it simply\n"
        "- do not add facts not present in the article\n\n"
        "Article:\n{article}"
    ),
)

PROMPTS: dict[str, PromptTemplate] = {
    SUMMARIZER_PROMPT_V1.version: SUMMARIZER_PROMPT_V1,
}

DEFAULT_SUMMARIZER_PROMPT_VERSION = SUMMARIZER_PROMPT_V1.version


def get_prompt(version: str | None = None) -> PromptTemplate:
    selected = version or DEFAULT_SUMMARIZER_PROMPT_VERSION
    try:
        return PROMPTS[selected]
    except KeyError as exc:
        available = ", ".join(sorted(PROMPTS))
        raise ValueError(f"Unknown prompt version '{selected}'. Available versions: {available}") from exc
