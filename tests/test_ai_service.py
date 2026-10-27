import base64
from types import SimpleNamespace

import ai_service
from config import AIConfig


class FakeAPIError(Exception):
    """Stand-in for the OpenAI SDK's APIError."""


def test_request_uses_configured_openai_compatible_client(monkeypatch):
    calls = {}

    class FakeResponses:
        def create(self, **kwargs):
            calls["request"] = kwargs
            return SimpleNamespace(output_text="Hello")

    class FakeOpenAI:
        def __init__(self, **kwargs):
            calls["client"] = kwargs
            self.responses = FakeResponses()

    monkeypatch.setitem(
        __import__("sys").modules,
        "openai",
        SimpleNamespace(OpenAI=FakeOpenAI, APIError=FakeAPIError),
    )
    config = AIConfig(
        api_key="test-key",
        base_url="https://api.example.test/v1",
        model="test-model",
        timeout_seconds=12.5,
    )

    result = ai_service.request_ai_response("Say hello", config)

    assert result == "Hello"
    assert calls["client"] == {
        "api_key": "test-key",
        "base_url": "https://api.example.test/v1",
        "timeout": 12.5,
    }
    assert calls["request"] == {
        "model": "test-model",
        "input": "Say hello",
    }


def test_request_loads_config_when_not_provided(monkeypatch):
    calls = {}
    config = AIConfig("test-key", "https://api.example.test/v1", "test-model", 5)

    class FakeResponses:
        def create(self, **kwargs):
            calls["request"] = kwargs
            return SimpleNamespace(output_text="Configured response")

    class FakeOpenAI:
        def __init__(self, **kwargs):
            calls["client"] = kwargs
            self.responses = FakeResponses()

    monkeypatch.setattr(ai_service, "load_ai_config", lambda: config)
    monkeypatch.setitem(
        __import__("sys").modules,
        "openai",
        SimpleNamespace(OpenAI=FakeOpenAI, APIError=FakeAPIError),
    )

    assert ai_service.request_ai_response("Prompt") == "Configured response"
    assert calls["request"]["model"] == "test-model"
    assert calls["request"]["input"] == "Prompt"


def test_request_wraps_api_failures_with_context(monkeypatch):
    config = AIConfig("test-key", "https://api.example.test/v1", "test-model", 5)
    failure = FakeAPIError("service unavailable")

    class FakeResponses:
        def create(self, **kwargs):
            raise failure

    class FakeOpenAI:
        def __init__(self, **kwargs):
            self.responses = FakeResponses()

    monkeypatch.setitem(
        __import__("sys").modules,
        "openai",
        SimpleNamespace(OpenAI=FakeOpenAI, APIError=FakeAPIError),
    )

    try:
        ai_service.request_ai_response("Prompt", config)
    except RuntimeError as exc:
        assert str(exc) == "AI API request failed: service unavailable"
        assert exc.__cause__ is failure
    else:
        raise AssertionError("API failures should be reported to the caller")


def test_request_does_not_wrap_unexpected_errors(monkeypatch):
    config = AIConfig("test-key", "https://api.example.test/v1", "test-model", 5)

    class FakeResponses:
        def create(self, **kwargs):
            raise ValueError("invalid test setup")

    class FakeOpenAI:
        def __init__(self, **kwargs):
            self.responses = FakeResponses()

    monkeypatch.setitem(
        __import__("sys").modules,
        "openai",
        SimpleNamespace(OpenAI=FakeOpenAI, APIError=FakeAPIError),
    )

    import pytest

    with pytest.raises(ValueError, match="invalid test setup"):
        ai_service.request_ai_response("Prompt", config)


def test_request_rejects_empty_response_text(monkeypatch):
    config = AIConfig("test-key", "https://api.example.test/v1", "test-model", 5)

    class FakeResponses:
        def create(self, **kwargs):
            return SimpleNamespace(output_text=" \t\n ")

    class FakeOpenAI:
        def __init__(self, **kwargs):
            self.responses = FakeResponses()

    monkeypatch.setitem(
        __import__("sys").modules,
        "openai",
        SimpleNamespace(OpenAI=FakeOpenAI, APIError=FakeAPIError),
    )

    import pytest

    with pytest.raises(RuntimeError, match="AI API returned an empty response"):
        ai_service.request_ai_response("Prompt", config)


def test_request_sends_validated_image_as_responses_input(monkeypatch, tmp_path):
    from PIL import Image

    path = tmp_path / "proof.png"
    Image.new("RGB", (2, 2), color="navy").save(path)
    calls = {}

    class FakeResponses:
        def create(self, **kwargs):
            calls["request"] = kwargs
            return SimpleNamespace(output_text="Image checked")

    class FakeOpenAI:
        def __init__(self, **kwargs):
            self.responses = FakeResponses()

    monkeypatch.setitem(
        __import__("sys").modules,
        "openai",
        SimpleNamespace(OpenAI=FakeOpenAI, APIError=FakeAPIError),
    )
    config = AIConfig("test-key", "https://api.example.test/v1", "vision-model", 5)

    result = ai_service.request_ai_response("Read this proof", config, path)

    content = calls["request"]["input"][0]["content"]
    assert result == "Image checked"
    assert calls["request"]["model"] == "vision-model"
    assert content[0] == {"type": "input_text", "text": "Read this proof"}
    assert content[1]["type"] == "input_image"
    assert content[1]["image_url"].startswith("data:image/png;base64,")
    payload = content[1]["image_url"].split(",", 1)[1]
    assert base64.b64decode(payload) == path.read_bytes()


def test_request_rejects_invalid_image_without_calling_api(monkeypatch, tmp_path):
    import pytest

    path = tmp_path / "invalid.png"
    path.write_bytes(b"not an image")
    calls = []

    class FakeResponses:
        def create(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(output_text="Should not be called")

    class FakeOpenAI:
        def __init__(self, **kwargs):
            self.responses = FakeResponses()

    monkeypatch.setitem(
        __import__("sys").modules,
        "openai",
        SimpleNamespace(OpenAI=FakeOpenAI, APIError=FakeAPIError),
    )
    config = AIConfig("test-key", "https://api.example.test/v1", "vision-model", 5)

    with pytest.raises(ValueError, match="not a valid, decodable image"):
        ai_service.request_ai_response("Inspect", config, path)

    assert calls == []
