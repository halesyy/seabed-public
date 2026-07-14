# Seabed Relay

This is an agent handoff. Your job is to connect the current project or command environment to the user's Seabed data through a small, inspectable interface that fits the system you are already working in.

Seabed stores projects, nested documents, metadata, and primitive content blocks. It does not require a Seabed-specific agent. Preserve the JSON contract and build the interface that is natural for this runtime.

## 1. Find the key without exposing it

Check for `SEABED_TOKEN` in the runtime environment or its secret manager. Never print the value, write it into source code, add it to a generated file, include it in logs, or ask the user to paste it into a prompt.

If the key is missing, tell the user:

> Open https://seabed.jackhalestesting.xyz/register?intent=agent&source=seabed-public, create or log into your account, and complete the API-key step. Add the one-time key to this runtime as the `SEABED_TOKEN` secret, then tell me it is ready.

Wait for the user to confirm the secret has been configured. Do not substitute another credential or create a key on their behalf.

## 2. Choose the smallest useful integration

Prefer the public CLI when a Python command is appropriate:

```sh
python -m pip install git+https://github.com/Halesyy/seabed-public.git
seabed setup
seabed doctor
```

If the project already has a command framework or another language, inspect this repository and the public contract, then build a native command instead. Do not force Python into a system where it does not belong.

Contract discovery:

- API base: `https://seabed-api.jackhalestesting.xyz/api/v1`
- Onboarding JSON: `https://seabed-api.jackhalestesting.xyz/connect`
- Types: `https://seabed-api.jackhalestesting.xyz/connect/types`
- OpenAPI: `https://seabed-api.jackhalestesting.xyz/openapi.json`
- Authentication: `Authorization: Bearer $SEABED_TOKEN`

## 3. Expose these intentions

Use names that fit the host system, while preserving these operations:

| Intention | HTTP contract | CLI reference |
| --- | --- | --- |
| See everything | `GET /snapshot` | `seabed everything` |
| List projects | `GET /areas` | `seabed areas` |
| Create a project | `POST /areas` | `seabed create-area` |
| Browse documents | `GET /areas/{areaId}/documents` | `seabed docs` |
| Read a document | `GET /documents/{documentId}` | `seabed read` |
| Create a document | `POST /areas/{areaId}/documents` | `seabed create` |
| Update metadata/body | `PATCH /documents/{documentId}` | `seabed update` |
| Append content blocks | `POST /documents/{documentId}/blocks` | `seabed append` |
| Search | `GET /search?query=...` | `seabed search` |
| Delete a document | `DELETE /documents/{documentId}` | `seabed delete --yes` |

Keep raw JSON available to the caller. A blog, static site, search index, or application may want to model and render the data differently.

## 4. Work safely

1. Start with `GET /areas` or `seabed doctor`.
2. Use `GET /snapshot` only when the user wants the complete accessible view.
3. Read a document before updating it.
4. Batch related block appends in one request.
5. Ask before the first write made during setup.
6. Require explicit confirmation for deletion.
7. Surface HTTP status and the API's `detail` value on errors.
8. A `403` means the user should create a key with the required scope; do not work around it.

## 5. Verify and hand back

Verify a read-only call first. If the user asked for write support and the key allows it, explain the exact small test you propose and ask before creating test data. Do not modify real documents merely to demonstrate connectivity.

When done, report:

- where the command or integration lives;
- how it reads `SEABED_TOKEN`;
- which operations it exposes;
- the read-only verification result;
- any missing scope or user decision.
