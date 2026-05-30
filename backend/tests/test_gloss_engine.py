from app.services.gloss import ASLGlossService
from app.services.tokenizer import EnglishTokenizer


def test_tokenizer_normalizes_case_and_possessives() -> None:
    tokens = EnglishTokenizer().tokenize("Earth's climate, NASA!")

    assert [token.normalized for token in tokens] == ["EARTH", "CLIMATE", "NASA"]


def test_rule_based_translation_matches_nasa_example() -> None:
    result = ASLGlossService().translate("Nasa launched a satellite.")

    assert result.gloss_tokens == ["NASA", "LAUNCH", "SATELLITE"]
    assert result.confidence == 1.0
    assert result.unknown_tokens == []


def test_tense_and_article_removal() -> None:
    result = ASLGlossService().translate("The students were watching the climate alerts.")

    assert result.gloss_tokens == ["STUDENT", "WATCH", "CLIMATE", "ALERT"]
    assert result.confidence == 1.0


def test_pronoun_handling() -> None:
    result = ASLGlossService().translate("She helped them with the app.")

    assert result.gloss_tokens == ["SHE", "HELP", "THEY", "APP"]


def test_unknown_token_handling_lowers_confidence() -> None:
    result = ASLGlossService().translate("NASA launched a quantum widget.")

    assert result.gloss_tokens == ["NASA", "LAUNCH", "QUANTUM", "WIDGET"]
    assert result.unknown_tokens == ["QUANTUM", "WIDGET"]
    assert result.confidence == 0.5


def test_generate_keeps_legacy_tuple_api() -> None:
    gloss, tokens = ASLGlossService().generate("NASA launched a satellite.")

    assert gloss == "NASA LAUNCH SATELLITE"
    assert tokens == ["NASA", "LAUNCH", "SATELLITE"]
