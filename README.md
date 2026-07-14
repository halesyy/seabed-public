# Seabed Public

A small, typed command-line interface for [Seabed](https://seabed.jackhalestesting.xyz). It gives people and agents a transparent way to list projects, read documents, search context, create content, and build their own interface over the Seabed Connect API.

The code intentionally stays close to HTTP. Typer provides the command surface, Pydantic validates public response types, and the Python standard library performs requests. There is no hidden agent and no required SDK.

## Start here

If you already have a Seabed API key, install the CLI and expose the key through your environment or secret store:

```sh
python -m pip install git+https://github.com/Halesyy/seabed-public.git
seabed setup
printf 'Seabed token: ' >&2
IFS= read -r -s SEABED_TOKEN
printf '\n' >&2
export SEABED_TOKEN
seabed doctor
```

If you do not have a key, use the agent/CLI onboarding path:

[Create a Seabed account and API key](https://seabed.jackhalestesting.xyz/register?intent=agent&source=seabed-public)

The final onboarding step displays the raw key once. Put it into `SEABED_TOKEN` or your agent runtime's secret store; do not commit it or paste it into a prompt.

## Commands

```text
seabed setup                         write ~/.config/seabed/config.json
seabed config                        show resolved non-secret config
seabed doctor                        verify the key with a read-only call
seabed everything                    return all areas and documents
seabed areas                         list projects/areas
seabed create-area "Research"        create a project/area
seabed docs --area AREA_ID           list root documents
seabed docs --area AREA_ID --recursive
seabed read DOCUMENT_ID              read one document
seabed create "Field notes" --area AREA_ID
seabed update DOCUMENT_ID --status in-progress
seabed append DOCUMENT_ID --text "New context"
seabed search "deployment"
seabed delete DOCUMENT_ID --yes
```

Every data command prints JSON. This makes the CLI useful on its own and easy for another command, agent, blog generator, search index, or automation to compose.

## Local JSON config

`seabed setup` writes a non-secret configuration file at `~/.config/seabed/config.json`:

```json
{
  "api_url": "https://seabed-api.jackhalestesting.xyz/api/v1",
  "default_area_id": null,
  "timeout_seconds": 30,
  "token_env": "SEABED_TOKEN"
}
```

Set `SEABED_CONFIG` to use another file. The API key is deliberately not stored in this JSON document.

## Seabed Relay: agent handoff

[Seabed Relay](SEABED_RELAY.md) is the ready-to-give agent connection brief. Give an agent the document URL and configure `SEABED_TOKEN` in its secret store. Relay explains the API intention, supported commands, types, safe write behaviour, and what to do when a key is missing.

```text
Use https://github.com/Halesyy/seabed-public/blob/main/SEABED_RELAY.md
to connect this workspace to Seabed. The API key is available as SEABED_TOKEN.
```

Do not replace the environment-variable sentence with the raw key.

## Public contracts

- [Human API guide](https://seabed.jackhalestesting.xyz/api)
- [Onboarding JSON](https://seabed-api.jackhalestesting.xyz/connect)
- [Type guide](https://seabed-api.jackhalestesting.xyz/connect/types)
- [OpenAPI](https://seabed-api.jackhalestesting.xyz/openapi.json)
- [Type modelling notes](docs/TYPES.md)

## Development

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/ruff check .
.venv/bin/pytest
.venv/bin/seabed --help
```

See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md) before opening a change.
