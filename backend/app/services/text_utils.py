import re


def split_sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]


def extract_summary(text: str, max_sentences: int = 2, max_chars: int = 260) -> str:
    sentences = split_sentences(text)
    summary = " ".join(sentences[:max_sentences]) if sentences else text[:max_chars]
    if len(summary) <= max_chars:
        return summary
    return summary[: max_chars - 3].rsplit(" ", 1)[0] + "..."


def simplify_english(text: str) -> str:
    replacements = {
        r"\bsuccessfully\b": "",
        r"\bapproximately\b": "about",
        r"\butilize\b": "use",
        r"\bassistance\b": "help",
        r"\bmonitoring\b": "watching",
    }
    simple = text
    for pattern, replacement in replacements.items():
        simple = re.sub(pattern, replacement, simple, flags=re.IGNORECASE)
    simple = re.sub(r"\s+", " ", simple).strip()
    if len(simple) <= 180:
        return simple
    return simple[:177].rsplit(" ", 1)[0] + "..."


def extract_labeled_line(content: str, label: str) -> str | None:
    match = re.search(rf"^{label}:\s*(.+)$", content, flags=re.MULTILINE)
    return match.group(1).strip() if match else None
