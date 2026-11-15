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


def test_status_command_updates_documents_and_folders(monkeypatch) -> None:
    observed: dict[str, object] = {}

    class RecordingClient:
        def request_model(self, _model, method, path, *, body=None, query=None):
            observed.update(method=method, path=path, body=body, query=query)
            return {"id": "folder-1", "kind": "folder", "status": body["status"]}

    monkeypatch.setattr("seabed_cli.cli._client", lambda *_args: RecordingClient())

    result = runner.invoke(app, ["status", "folder-1", "completed"])

    assert result.exit_code == 0, result.output
    assert observed == {
        "method": "PATCH",
        "path": "/documents/folder-1",
        "body": {"status": "completed"},
        "query": None,
    }
    assert json.loads(result.stdout)["status"] == "completed"


def test_status_command_rejects_unknown_status_before_network(monkeypatch) -> None:
    def unexpected_client(*_args):
        raise AssertionError("invalid status should fail before resolving a client")

    monkeypatch.setattr("seabed_cli.cli._client", unexpected_client)

    result = runner.invoke(app, ["status", "document-1", "paused"])

    assert result.exit_code != 0
    assert "paused" in result.output
