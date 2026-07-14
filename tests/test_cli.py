from __future__ import annotations

import json

from typer.testing import CliRunner

from seabed_cli.cli import app

runner = CliRunner()


def test_config_command_is_secret_free(tmp_path, monkeypatch) -> None:
    path = tmp_path / "config.json"
    monkeypatch.setenv("SEABED_CONFIG", str(path))
    monkeypatch.setenv("SEABED_TOKEN", "must-not-appear")

    result = runner.invoke(app, ["config"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["token_env"] == "SEABED_TOKEN"
    assert "must-not-appear" not in result.stdout


def test_destructive_command_requires_confirmation() -> None:
    result = runner.invoke(app, ["delete", "document-1"])

    assert result.exit_code != 0
    assert "Deletion is permanent" in result.output
