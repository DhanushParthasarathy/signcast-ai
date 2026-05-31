import importlib


def test_sign_dictionary_and_sequence_modules_import_without_cycle() -> None:
    sign_dictionary = importlib.import_module("app.repositories.sign_dictionary")
    sign_sequence = importlib.import_module("app.services.sign_sequence")

    assert hasattr(sign_dictionary, "SignDictionaryRepository")
    assert hasattr(sign_sequence, "SignSequenceService")


def test_fastapi_app_imports_without_circular_import_failure() -> None:
    module = importlib.import_module("app.main")

    assert hasattr(module, "app")
