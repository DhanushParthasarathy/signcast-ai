from dataclasses import dataclass, field

from app.services.tokenizer import Token


ARTICLES = {"A", "AN", "THE"}

AUXILIARY_TENSE_MARKERS = {
    "AM",
    "ARE",
    "BE",
    "BEEN",
    "BEING",
    "DID",
    "DO",
    "DOES",
    "HAD",
    "HAS",
    "HAVE",
    "IS",
    "WAS",
    "WERE",
    "WILL",
    "WOULD",
}

PREPOSITIONS_AND_FILLERS = {
    "ABOUT",
    "AND",
    "AT",
    "BY",
    "FOR",
    "FROM",
    "IN",
    "INTO",
    "OF",
    "ON",
    "OR",
    "THAN",
    "THAT",
    "THIS",
    "TO",
    "WITH",
}

PRONOUN_MAP = {
    "I": "ME",
    "ME": "ME",
    "MY": "ME",
    "MINE": "ME",
    "YOU": "YOU",
    "YOUR": "YOU",
    "YOURS": "YOU",
    "HE": "HE",
    "HIM": "HE",
    "HIS": "HE",
    "SHE": "SHE",
    "HER": "SHE",
    "HERS": "SHE",
    "WE": "WE",
    "US": "WE",
    "OUR": "WE",
    "THEY": "THEY",
    "THEM": "THEY",
    "THEIR": "THEY",
    "IT": "",
    "ITS": "",
}

LEXICAL_NORMALIZATION = {
    "ADDED": "ADD",
    "ALERTS": "ALERT",
    "BUILT": "BUILD",
    "CREATED": "CREATE",
    "CREATES": "CREATE",
    "DELAYS": "DELAY",
    "EXPANDED": "EXPAND",
    "EXPANDS": "EXPAND",
    "HELPED": "HELP",
    "HELPS": "HELP",
    "LAUNCHED": "LAUNCH",
    "LAUNCHES": "LAUNCH",
    "LAUNCHING": "LAUNCH",
    "MONITOR": "WATCH",
    "MONITORED": "WATCH",
    "MONITORING": "WATCH",
    "NASA": "NASA",
    "NEW": "",
    "SATELLITES": "SATELLITE",
    "SUCCESSFUL": "",
    "SUCCESSFULLY": "",
    "WATCHING": "WATCH",
}

KNOWN_GLOSS_TOKENS = {
    "ACCESSIBILITY",
    "ADD",
    "ALERT",
    "APP",
    "BUILD",
    "BUS",
    "CITY",
    "CLIMATE",
    "CREATE",
    "DATA",
    "DELAY",
    "EARTH",
    "EXPAND",
    "HE",
    "HELP",
    "HOSPITAL",
    "LAUNCH",
    "ME",
    "NASA",
    "NEWS",
    "PATIENT",
    "SATELLITE",
    "SCHOOL",
    "SCIENTIST",
    "SIGN",
    "STUDENT",
    "THEY",
    "TRAIN",
    "WATCH",
    "WE",
    "YOU",
}


@dataclass(frozen=True)
class RuleDecision:
    gloss_tokens: list[str] = field(default_factory=list)
    consumed: bool = True
    known: bool = True


class GlossRuleSet:
    def translate_token(self, token: Token) -> RuleDecision:
        word = token.normalized
        if word in ARTICLES or word in AUXILIARY_TENSE_MARKERS or word in PREPOSITIONS_AND_FILLERS:
            return RuleDecision([])

        if word in PRONOUN_MAP:
            mapped = PRONOUN_MAP[word]
            return RuleDecision([mapped] if mapped else [])

        normalized = LEXICAL_NORMALIZATION.get(word)
        if normalized is not None:
            return RuleDecision([normalized] if normalized else [], known=bool(normalized))

        stemmed = self._stem_verb_tense(word)
        if stemmed in KNOWN_GLOSS_TOKENS:
            return RuleDecision([stemmed])

        if word in KNOWN_GLOSS_TOKENS:
            return RuleDecision([word])

        return RuleDecision([word], known=False)

    def _stem_verb_tense(self, word: str) -> str:
        if len(word) > 5 and word.endswith("ING"):
            return word[:-3]
        if len(word) > 4 and word.endswith("ED"):
            return word[:-2]
        if len(word) > 4 and word.endswith("ES"):
            return word[:-2]
        if len(word) > 3 and word.endswith("S"):
            return word[:-1]
        return word
