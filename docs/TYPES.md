# Seabed public types

Seabed's stable public model has three levels:

```text
Area (a project)
└── Document (metadata, hierarchy, body)
    └── Block[] (ordered primitive content)
```

The canonical machine-readable guide is [`GET /connect/types`](https://seabed-api.jackhalestesting.xyz/connect/types), and the complete request/response schema is in [OpenAPI](https://seabed-api.jackhalestesting.xyz/openapi.json).

## Areas

An area is the API name for a Seabed project. It has a stable `id`, user-scoped `slug`, optional description, Unix-second timestamps, and token-derived permissions.

## Documents

Documents include hierarchy (`parentDocumentId`, `path`, `depth`), plain `body` text, ordered `blocks`, tags, source and summary fields, presentation metadata, workflow status, value/ranking fields, dates, timestamps, and permissions.

The Pydantic model in [`src/seabed_cli/models.py`](../src/seabed_cli/models.py) parses the complete public response while allowing future additive fields.

## Blocks

Every returned block has a server-generated `id` and a discriminating `type`:

- `header`: heading text and level 1–3;
- `text`: standard editable text plus formatting ranges;
- `paragraph`: paragraph-compatible text;
- `image`: URL, alt text, caption, and optional dimensions;
- `attachment`: file URL and transport metadata;
- `link`: labelled internal or external link;
- `diagram`: renderer-owned nodes, edges, type, title, and viewport.

When writing, omit `id`; Seabed creates it. Unknown block fields are rejected so an integration fails loudly instead of silently losing information.

## Time and nullability

All Unix values are seconds, not milliseconds. Nullable metadata can be omitted during document creation. Preserve unknown response fields if your downstream system proxies or re-emits the source JSON.
