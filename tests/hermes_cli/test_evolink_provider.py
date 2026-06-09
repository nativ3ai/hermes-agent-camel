"""Tests for Evolink provider support."""

import os

import pytest

from hermes_cli.auth import (
    PROVIDER_REGISTRY,
    resolve_provider,
    get_api_key_provider_status,
    resolve_api_key_provider_credentials,
)


# =============================================================================
# Provider Registry
# =============================================================================


class TestEvolinkProviderRegistry:
    """Verify Evolink is registered correctly in the PROVIDER_REGISTRY."""

    def test_registered(self):
        assert "evolink" in PROVIDER_REGISTRY

    def test_name(self):
        assert PROVIDER_REGISTRY["evolink"].name == "Evolink"

    def test_auth_type(self):
        assert PROVIDER_REGISTRY["evolink"].auth_type == "api_key"

    def test_inference_base_url(self):
        assert PROVIDER_REGISTRY["evolink"].inference_base_url == "https://direct.evolink.ai/v1"

    def test_api_key_env_vars(self):
        assert PROVIDER_REGISTRY["evolink"].api_key_env_vars == ("EVOLINK_API_KEY",)

    def test_base_url_env_var(self):
        assert PROVIDER_REGISTRY["evolink"].base_url_env_var == "EVOLINK_BASE_URL"


# =============================================================================
# Aliases
# =============================================================================


class TestEvolinkAliases:
    """All aliases should resolve to 'evolink'."""

    @pytest.mark.parametrize("alias", [
        "evolink", "evolinkai",
    ])
    def test_alias_resolves(self, alias, monkeypatch):
        # Clear env to avoid auto-detection interfering
        for key in ("EVOLINK_API_KEY",):
            monkeypatch.delenv(key, raising=False)
        monkeypatch.setenv("EVOLINK_API_KEY", "sk-test-key-12345678")
        assert resolve_provider(alias) == "evolink"

    def test_normalize_provider_models_py(self):
        from hermes_cli.models import normalize_provider
        assert normalize_provider("evolinkai") == "evolink"

    def test_normalize_provider_providers_py(self):
        from hermes_cli.providers import normalize_provider
        assert normalize_provider("evolinkai") == "evolink"


# =============================================================================
# Auto-detection
# =============================================================================


class TestEvolinkAutoDetection:
    """Setting EVOLINK_API_KEY should auto-detect the provider."""

    def test_auto_detect(self, monkeypatch):
        # Clear all other provider env vars
        for var in ("OPENROUTER_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
                     "DEEPSEEK_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY",
                     "DASHSCOPE_API_KEY", "XAI_API_KEY", "KIMI_API_KEY",
                     "MINIMAX_API_KEY", "AI_GATEWAY_API_KEY", "KILOCODE_API_KEY",
                     "HF_TOKEN", "GLM_API_KEY", "COPILOT_GITHUB_TOKEN",
                     "GH_TOKEN", "GITHUB_TOKEN", "MINIMAX_CN_API_KEY",
                     "TOKENHUB_API_KEY", "ARCEEAI_API_KEY",
                     "XIAOMI_API_KEY", "GMI_API_KEY", "AZURE_FOUNDRY_API_KEY",
                     "OPENCODE_ZEN_API_KEY", "OPENCODE_GO_API_KEY"):
            monkeypatch.delenv(var, raising=False)
        monkeypatch.setenv("EVOLINK_API_KEY", "sk-evolink-test-12345678")
        provider = resolve_provider("auto")
        assert provider == "evolink"


# =============================================================================
# Credentials
# =============================================================================


class TestEvolinkCredentials:
    """Test credential resolution for the evolink provider."""

    def test_status_configured(self, monkeypatch):
        monkeypatch.setenv("EVOLINK_API_KEY", "sk-test-12345678")
        status = get_api_key_provider_status("evolink")
        assert status["configured"]

    def test_status_not_configured(self, monkeypatch):
        monkeypatch.delenv("EVOLINK_API_KEY", raising=False)
        status = get_api_key_provider_status("evolink")
        assert not status["configured"]

    def test_resolve_credentials(self, monkeypatch):
        monkeypatch.setenv("EVOLINK_API_KEY", "sk-test-12345678")
        monkeypatch.delenv("EVOLINK_BASE_URL", raising=False)
        creds = resolve_api_key_provider_credentials("evolink")
        assert creds["api_key"] == "sk-test-12345678"
        assert creds["base_url"] == "https://direct.evolink.ai/v1"

    def test_custom_base_url_override(self, monkeypatch):
        monkeypatch.setenv("EVOLINK_API_KEY", "sk-test-12345678")
        monkeypatch.setenv("EVOLINK_BASE_URL", "https://custom.evolink.example/v1")
        creds = resolve_api_key_provider_credentials("evolink")
        assert creds["base_url"] == "https://custom.evolink.example/v1"


# =============================================================================
# Model catalog (dynamic — no static list)
# =============================================================================


class TestEvolinkModelCatalog:
    """Evolink uses dynamic model discovery via models.dev."""

    def test_models_dev_mapping(self):
        from agent.models_dev import PROVIDER_TO_MODELS_DEV
        assert PROVIDER_TO_MODELS_DEV["evolink"] == "evolink"

    def test_static_model_list_fallback(self):
        """Static _PROVIDER_MODELS fallback must exist for model picker.

        We only assert the provider key is present — the specific model
        names are data that changes with upstream releases and doesn't
        belong in tests.
        """
        from hermes_cli.models import _PROVIDER_MODELS
        assert "evolink" in _PROVIDER_MODELS
        assert len(_PROVIDER_MODELS["evolink"]) >= 1

    def test_list_agentic_models_mock(self, monkeypatch):
        """When models.dev returns Evolink data, list_agentic_models should return models."""
        from agent import models_dev as md

        fake_data = {
            "evolink": {
                "name": "Evolink",
                "api": "https://direct.evolink.ai/v1",
                "env": ["EVOLINK_API_KEY"],
                "models": {
                    "gpt-5.2": {
                        "limit": {"context": 1050000},
                        "tool_call": True,
                    },
                    "gemini-2.5-pro": {
                        "limit": {"context": 1000000},
                        "tool_call": True,
                    },
                    "deepseek-v4-pro": {
                        "limit": {"context": 1000000},
                        "tool_call": True,
                    },
                },
            }
        }
        monkeypatch.setattr(md, "fetch_models_dev", lambda: fake_data)

        result = md.list_agentic_models("evolink")
        assert "gpt-5.2" in result
        assert "gemini-2.5-pro" in result


# =============================================================================
# Normalization
# =============================================================================


class TestEvolinkNormalization:
    """Model name normalization — Evolink is an aggregator provider."""

    def test_matching_prefix_strip(self):
        """evolink/openai/gpt-5.2 should strip the evolink prefix for direct API."""
        from hermes_cli.model_normalize import _MATCHING_PREFIX_STRIP_PROVIDERS
        assert "evolink" in _MATCHING_PREFIX_STRIP_PROVIDERS

    def test_normalize_strips_provider_prefix(self):
        from hermes_cli.model_normalize import normalize_model_for_provider
        result = normalize_model_for_provider("evolink/openai/gpt-5.2", "evolink")
        assert result == "openai/gpt-5.2"

    def test_normalize_bare_name_unchanged(self):
        from hermes_cli.model_normalize import normalize_model_for_provider
        result = normalize_model_for_provider("openai/gpt-5.2", "evolink")
        assert result == "openai/gpt-5.2"

    @pytest.mark.parametrize("empty_input", ["", None, "   "])
    def test_normalize_empty_and_none(self, empty_input):
        """None, empty, and whitespace-only inputs return empty string."""
        from hermes_cli.model_normalize import normalize_model_for_provider
        result = normalize_model_for_provider(empty_input, "evolink")
        assert result == ""


# =============================================================================
# URL mapping
# =============================================================================


class TestEvolinkURLMapping:
    """Test URL → provider inference for Evolink endpoints."""

    def test_url_to_provider(self):
        from agent.model_metadata import _URL_TO_PROVIDER
        assert _URL_TO_PROVIDER.get("direct.evolink.ai") == "evolink"

    def test_provider_prefixes(self):
        from agent.model_metadata import _PROVIDER_PREFIXES
        assert "evolink" in _PROVIDER_PREFIXES

    def test_infer_from_url(self):
        from agent.model_metadata import _infer_provider_from_url
        assert _infer_provider_from_url("https://direct.evolink.ai/v1") == "evolink"


# =============================================================================
# providers.py
# =============================================================================


class TestEvolinkProvidersModule:
    """Test Evolink in the unified providers module."""

    def test_overlay_exists(self):
        from hermes_cli.providers import HERMES_OVERLAYS
        assert "evolink" in HERMES_OVERLAYS
        overlay = HERMES_OVERLAYS["evolink"]
        assert overlay.transport == "openai_chat"
        assert overlay.base_url_env_var == "EVOLINK_BASE_URL"
        assert not overlay.is_aggregator

    def test_alias_resolves(self):
        from hermes_cli.providers import normalize_provider
        assert normalize_provider("evolinkai") == "evolink"

    def test_label(self):
        from hermes_cli.providers import get_label
        assert get_label("evolink") == "Evolink"


# =============================================================================
# Doctor
# =============================================================================


class TestEvolinkDoctor:
    """Verify hermes doctor recognizes Evolink env vars."""

    def test_provider_env_hints(self):
        from hermes_cli.doctor import _PROVIDER_ENV_HINTS
        assert "EVOLINK_API_KEY" in _PROVIDER_ENV_HINTS


class TestEvolinkAgentInit:
    """Verify the agent can be constructed with evolink provider without errors."""

    def test_no_syntax_errors(self):
        """Importing run_agent with evolink should not raise."""
        import importlib
        importlib.import_module("run_agent")

    def test_api_mode_is_chat_completions(self):
        from hermes_cli.providers import HERMES_OVERLAYS, TRANSPORT_TO_API_MODE
        overlay = HERMES_OVERLAYS["evolink"]
        api_mode = TRANSPORT_TO_API_MODE[overlay.transport]
        assert api_mode == "chat_completions"
