from __future__ import annotations

import json
import os
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

DEFAULT_API_URL = "https://seabed-api.jackhalestesting.xyz/api/v1"


class SeabedConfig(BaseModel):
    """Non-secret local preferences for the Seabed CLI."""

    model_config = ConfigDict(extra="forbid", validate_default=True)

    api_url: HttpUrl = Field(default=DEFAULT_API_URL)
    token_env: str = Field(default="SEABED_TOKEN", pattern=r"^[A-Z_][A-Z0-9_]*$")
    default_area_id: str | None = None
    timeout_seconds: float = Field(default=30, gt=0, le=120)

    @classmethod
    def load(cls, path: Path | None = None) -> SeabedConfig:
        config_path = path or config_path_from_environment()
        if not config_path.exists():
            return cls()
        return cls.model_validate_json(config_path.read_text(encoding="utf-8"))

    def save(self, path: Path | None = None) -> Path:
        config_path = path or config_path_from_environment()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(self.model_dump(mode="json"), indent=2, sort_keys=True) + "\n"
        config_path.write_text(payload, encoding="utf-8")
        config_path.chmod(0o600)
        return config_path


def config_path_from_environment() -> Path:
    override = os.environ.get("SEABED_CONFIG")
    if override:
        return Path(override).expanduser()
    config_home = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return config_home / "seabed" / "config.json"
