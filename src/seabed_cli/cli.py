from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any

import typer
from pydantic import BaseModel, ValidationError

from seabed_cli.client import MissingTokenError, SeabedApiError, SeabedClient
from seabed_cli.config import DEFAULT_API_URL, SeabedConfig, config_path_from_environment
from seabed_cli.models import (
    AppendBlocksResponse,
    Area,
    AreaListResponse,
    DeleteResponse,
    Document,
    DocumentKind,
    DocumentListResponse,
    DocumentStatus,
    SnapshotResponse,
)

app = typer.Typer(
    name="seabed",
    help="Read and write your Seabed data from a small, inspectable CLI.",
    no_args_is_help=True,
    add_completion=False,
)


@app.command()
def setup(
    api_url: Annotated[str, typer.Option(help="Seabed Connect API base URL.")] = DEFAULT_API_URL,
    token_env: Annotated[
        str, typer.Option(help="Environment variable containing the API key.")
    ] = "SEABED_TOKEN",
    default_area: Annotated[str | None, typer.Option(help="Optional default area ID.")] = None,
) -> None:
    """Write a non-secret JSON config file."""
    config = SeabedConfig(api_url=api_url, token_env=token_env, default_area_id=default_area)
    path = config.save()
    typer.echo(f"Saved config to {path}")
    typer.echo(f"The API key is not stored there. Put it in {config.token_env} or your secret store.")


@app.command("config")
def show_config() -> None:
    """Show the resolved local configuration without exposing a key."""
    config = SeabedConfig.load()
    payload = config.model_dump(mode="json")
    payload["path"] = str(config_path_from_environment())
    _emit(payload)


@app.command()
def doctor() -> None:
    """Verify the API key and connection with a read-only request."""
    response = _client().request_model(AreaListResponse, "GET", "/areas")
    typer.echo(f"Connected. The key can read {response.count} area(s).")


@app.command()
def everything() -> None:
    """Return every accessible area and document."""
    response = _client().request_model(SnapshotResponse, "GET", "/snapshot")
    _emit(response)


@app.command()
def areas() -> None:
    """List projects, called areas by the Connect API."""
    response = _client().request_model(AreaListResponse, "GET", "/areas")
    _emit(response)


@app.command("create-area")
def create_area(
    name: Annotated[str, typer.Argument(help="Project/area name.")],
    description: Annotated[str | None, typer.Option(help="Optional area description.")] = None,
) -> None:
    """Create a project/area."""
    response = _client().request_model(
        Area,
        "POST",
        "/areas",
        body={"name": name, "description": description},
    )
    _emit(response)


@app.command()
def docs(
    area: Annotated[str | None, typer.Option(help="Area ID; falls back to config.")] = None,
    parent: Annotated[str | None, typer.Option(help="Only list children of this document.")] = None,
    recursive: Annotated[bool, typer.Option("--recursive/--roots-only")] = False,
) -> None:
    """List documents in an area."""
    config = SeabedConfig.load()
    area_id = _require_area(area, config)
    response = _client(config).request_model(
        DocumentListResponse,
        "GET",
        f"/areas/{area_id}/documents",
        query={"parentDocumentId": parent, "recursive": recursive},
    )
    _emit(response)


@app.command("read")
def read_document(
    document_id: Annotated[str, typer.Argument(help="Document ID.")],
) -> None:
    """Read one document."""
    response = _client().request_model(Document, "GET", f"/documents/{document_id}")
    _emit(response)


@app.command("create")
def create_document(
    title: Annotated[str, typer.Argument(help="Document title.")],
    area: Annotated[str | None, typer.Option(help="Area ID; falls back to config.")] = None,
    kind: Annotated[DocumentKind, typer.Option(help="Semantic document kind.")] = "note",
    parent: Annotated[str | None, typer.Option(help="Optional parent document ID.")] = None,
    body: Annotated[str | None, typer.Option(help="Plain body text.")] = None,
    body_file: Annotated[Path | None, typer.Option(exists=True, dir_okay=False)] = None,
    tags: Annotated[list[str] | None, typer.Option("--tag", help="Repeat for multiple tags.")] = None,
) -> None:
    """Create a document."""
    config = SeabedConfig.load()
    area_id = _require_area(area, config)
    response = _client(config).request_model(
        Document,
        "POST",
        f"/areas/{area_id}/documents",
        body={
            "title": title,
            "kind": kind,
            "parentDocumentId": parent,
            "body": _text(body, body_file),
            "tags": tags or [],
        },
    )
    _emit(response)


@app.command("update")
def update_document(
    document_id: Annotated[str, typer.Argument(help="Document ID.")],
    title: Annotated[str | None, typer.Option(help="New title.")] = None,
    body: Annotated[str | None, typer.Option(help="New plain body text.")] = None,
    body_file: Annotated[Path | None, typer.Option(exists=True, dir_okay=False)] = None,
    status: Annotated[DocumentStatus | None, typer.Option(help="New workflow status.")] = None,
    summary: Annotated[str | None, typer.Option(help="New short summary.")] = None,
) -> None:
    """Update selected document fields."""
    payload: dict[str, Any] = {
        key: value
        for key, value in {"title": title, "status": status, "summary": summary}.items()
        if value is not None
    }
    if body is not None or body_file is not None:
        payload["body"] = _text(body, body_file)
    if not payload:
        raise typer.BadParameter("Provide --title, --body, --body-file, --status, or --summary.")
    response = _client().request_model(
        Document,
        "PATCH",
        f"/documents/{document_id}",
        body=payload,
    )
    _emit(response)


@app.command("append")
def append_blocks(
    document_id: Annotated[str, typer.Argument(help="Document ID.")],
    text: Annotated[str | None, typer.Option(help="Append one text block.")] = None,
    blocks_file: Annotated[Path | None, typer.Option(exists=True, dir_okay=False)] = None,
) -> None:
    """Append text or a JSON block batch."""
    if (text is None) == (blocks_file is None):
        raise typer.BadParameter("Provide exactly one of --text or --blocks-file.")
    blocks: Any
    if blocks_file is not None:
        blocks = json.loads(blocks_file.read_text(encoding="utf-8"))
        if isinstance(blocks, dict) and "blocks" in blocks:
            blocks = blocks["blocks"]
        if not isinstance(blocks, list):
            raise typer.BadParameter('The block file must contain a JSON array or {"blocks": [...] }.')
    else:
        blocks = [{"type": "text", "text": text, "formatting": []}]
    response = _client().request_model(
        AppendBlocksResponse,
        "POST",
        f"/documents/{document_id}/blocks",
        body={"blocks": blocks},
    )
    _emit(response)


@app.command()
def search(
    query: Annotated[str, typer.Argument(help="Text to find.")],
    area: Annotated[str | None, typer.Option(help="Optional area ID.")] = None,
    limit: Annotated[int, typer.Option(min=1, max=50)] = 25,
) -> None:
    """Search accessible documents."""
    response = _client().request_model(
        DocumentListResponse,
        "GET",
        "/search",
        query={"query": query, "areaId": area, "limit": limit},
    )
    _emit(response)


@app.command("delete")
def delete_document(
    document_id: Annotated[str, typer.Argument(help="Document ID.")],
    yes: Annotated[bool, typer.Option("--yes", help="Confirm permanent deletion.")] = False,
) -> None:
    """Permanently delete a document."""
    if not yes:
        raise typer.BadParameter("Deletion is permanent. Re-run with --yes.")
    response = _client().request_model(
        DeleteResponse,
        "DELETE",
        f"/documents/{document_id}",
    )
    _emit(response)


def _client(config: SeabedConfig | None = None) -> SeabedClient:
    return SeabedClient.from_environment(config)


def _require_area(area: str | None, config: SeabedConfig) -> str:
    area_id = area or config.default_area_id
    if not area_id:
        raise typer.BadParameter("Provide --area or set default_area_id with `seabed setup`.")
    return area_id


def _text(value: str | None, path: Path | None) -> str:
    if path is not None:
        if value is not None:
            raise typer.BadParameter("Use either --body or --body-file, not both.")
        return path.read_text(encoding="utf-8")
    return value or ""


def _emit(value: BaseModel | dict[str, Any]) -> None:
    payload = value.model_dump(mode="json") if isinstance(value, BaseModel) else value
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


def main() -> None:
    try:
        app()
    except (MissingTokenError, SeabedApiError, RuntimeError, ValidationError) as exc:
        typer.echo(str(exc), err=True)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
