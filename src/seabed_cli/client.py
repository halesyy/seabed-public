from __future__ import annotations

import json
import os
from typing import Any, TypeVar
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from pydantic import BaseModel

from seabed_cli.config import SeabedConfig

ResponseModel = TypeVar("ResponseModel", bound=BaseModel)
SIGNUP_URL = "https://seabed.jackhalestesting.xyz/register?intent=agent&source=seabed-public"


class MissingTokenError(RuntimeError):
    pass


class SeabedApiError(RuntimeError):
    def __init__(self, status: int, detail: Any):
        self.status = status
        self.detail = detail
        super().__init__(f"Seabed returned HTTP {status}: {detail}")


class SeabedClient:
    """A deliberately small HTTP client that keeps the Seabed contract visible."""

    def __init__(self, config: SeabedConfig, token: str):
        self.config = config
        self.token = token

    @classmethod
    def from_environment(cls, config: SeabedConfig | None = None) -> SeabedClient:
        loaded = config or SeabedConfig.load()
        token = os.environ.get(loaded.token_env)
        if not token:
            raise MissingTokenError(
                f"{loaded.token_env} is not set. Create an account and API key at {SIGNUP_URL}, "
                "then add the key to your environment or secret store."
            )
        return cls(loaded, token)

    def request(
        self,
        method: str,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        query: dict[str, str | int | bool | None] | None = None,
    ) -> Any:
        base_url = str(self.config.api_url).rstrip("/")
        clean_path = path if path.startswith("/") else f"/{path}"
        url = f"{base_url}{clean_path}"
        if query:
            encoded = urlencode(
                {
                    key: str(value).lower() if isinstance(value, bool) else value
                    for key, value in query.items()
                    if value is not None
                }
            )
            if encoded:
                url = f"{url}?{encoded}"

        data = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "seabed-public/0.1.0",
        }
        if data is not None:
            headers["Content-Type"] = "application/json"

        request = Request(url, data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=self.config.timeout_seconds) as response:
                return _decode(response.read())
        except HTTPError as exc:
            payload = _decode(exc.read())
            detail = payload.get("detail", payload) if isinstance(payload, dict) else payload
            raise SeabedApiError(exc.code, detail) from exc
        except URLError as exc:
            raise RuntimeError(f"Could not reach Seabed: {exc.reason}") from exc

    def request_model(
        self,
        model: type[ResponseModel],
        method: str,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        query: dict[str, str | int | bool | None] | None = None,
    ) -> ResponseModel:
        return model.model_validate(self.request(method, path, body=body, query=query))


def _decode(raw: bytes) -> Any:
    if not raw:
        return None
    text = raw.decode("utf-8", errors="replace")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text
