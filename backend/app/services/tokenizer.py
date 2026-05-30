import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    original: str
    normalized: str
    index: int


class EnglishTokenizer:
    TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")

    def tokenize(self, text: str) -> list[Token]:
        tokens: list[Token] = []
        for index, match in enumerate(self.TOKEN_PATTERN.finditer(text)):
            original = match.group(0)
            normalized = normalize_token(original)
            if normalized:
                tokens.append(Token(original=original, normalized=normalized, index=index))
        return tokens


def normalize_token(token: str) -> str:
    cleaned = token.strip().upper()
    possessive = cleaned.endswith("'S")
    if possessive:
        cleaned = cleaned[:-2]
    return re.sub(r"[^A-Z0-9]", "", cleaned)
