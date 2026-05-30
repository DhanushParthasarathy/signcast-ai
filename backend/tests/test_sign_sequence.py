from app.services.sign_sequence import SignSequenceService


def test_generate_sign_sequence_marks_missing_tokens() -> None:
    service = SignSequenceService(dictionary={"NASA": "/signs/nasa.mp4"})

    sequence, missing = service.generate("NASA CLIMATE")

    assert sequence[0].clip_url == "/signs/nasa.mp4"
    assert sequence[0].status == "ready"
    assert sequence[1].status == "missing"
    assert missing == ["CLIMATE"]
