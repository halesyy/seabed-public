from __future__ import annotations

import pytest

from seabed_cli.client import SIGNUP_URL, MissingTokenError, SeabedApiError, SeabedClient
from seabed_cli.config import SeabedConfig


def test_missing_token_points_to_agent_onboarding(monkeypatch) -> None:
    monkeypatch.delenv("SEABED_TOKEN", raising=False)

    with pytest.raises(MissingTokenError, match="SEABED_TOKEN") as caught:
        SeabedClient.from_environment(SeabedConfig())

    assert SIGNUP_URL in str(caught.value)


def test_client_reads_configured_token_environment(monkeypatch) -> None:
    monkeypatch.setenv("MY_SEABED_KEY", "secret-test-key")

    client = SeabedClient.from_environment(SeabedConfig(token_env="MY_SEABED_KEY"))

    assert client.token == "secret-test-key"


def test_api_error_includes_status_and_detail() -> None:
    error = SeabedApiError(422, "Area name is required")

    assert str(error) == "Seabed returned HTTP 422: Area name is required"
