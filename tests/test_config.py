import pytest

from config import AIConfig, AI_MODEL, load_ai_config


def test_loads_provider_independent_ai_settings():
    config = load_ai_config({
        "AI_API_KEY": "local-test-key",
        "AI_API_BASE_URL": "https://api.example.test/v1",
        "AI_MODEL": "vision-model",
        "AI_TIMEOUT_SECONDS": "12.5",
    })

    assert config == AIConfig("local-test-key", "https://api.example.test/v1", "vision-model", 12.5)
    assert "local-test-key" not in repr(config)


def test_requires_key_and_endpoint():
    with pytest.raises(ValueError, match="AI_API_KEY"):
        load_ai_config({})


def test_uses_default_model_when_not_configured():
    config = load_ai_config({
        "AI_API_KEY": "key",
        "AI_API_BASE_URL": "https://api.example.test",
    })
    assert config.model == AI_MODEL == "nvidia/nemotron-3.5-super-vl:free"


@pytest.mark.parametrize("url", ["", "api.example.test", "ftp://api.example.test"])
def test_rejects_invalid_endpoint(url):
    with pytest.raises(ValueError, match="AI_API_BASE_URL"):
        load_ai_config({
            "AI_API_KEY": "key",
            "AI_API_BASE_URL": url,
            "AI_MODEL": "model",
        })


@pytest.mark.parametrize("timeout", ["0", "-1", "invalid", "nan", "inf"])
def test_rejects_invalid_timeout(timeout):
    with pytest.raises(ValueError, match="AI_TIMEOUT_SECONDS"):
        load_ai_config({
            "AI_API_KEY": "key",
            "AI_API_BASE_URL": "https://api.example.test",
            "AI_MODEL": "model",
            "AI_TIMEOUT_SECONDS": timeout,
        })
