from __future__ import annotations

import json

from seabed_cli.config import DEFAULT_API_URL, SeabedConfig


def test_config_round_trip_does_not_contain_a_token(tmp_path) -> None:
    path = tmp_path / "config.json"
    config = SeabedConfig(default_area_id="area-1")

    saved = config.save(path)
    loaded = SeabedConfig.load(path)

    assert saved == path
    assert loaded.default_area_id == "area-1"
    assert str(loaded.api_url).rstrip("/") == DEFAULT_API_URL
    assert "token" not in json.loads(path.read_text())
    assert path.stat().st_mode & 0o777 == 0o600


def test_missing_config_uses_safe_defaults(tmp_path) -> None:
    config = SeabedConfig.load(tmp_path / "missing.json")

    assert config.token_env == "SEABED_TOKEN"
    assert config.default_area_id is None
