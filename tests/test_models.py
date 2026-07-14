from __future__ import annotations

from seabed_cli.models import Document, SnapshotResponse


def test_document_parses_discriminated_blocks_and_future_fields() -> None:
    document = Document.model_validate(
        {
            "id": "document-1",
            "areaId": "area-1",
            "title": "Field notes",
            "body": "",
            "kind": "note",
            "parentDocumentId": None,
            "path": [],
            "depth": 0,
            "sortOrder": 0,
            "tags": ["research"],
            "sourceUrl": None,
            "summary": None,
            "icon": None,
            "color": None,
            "blocks": [{"id": "block-1", "type": "header", "level": 2, "text": "Findings"}],
            "status": None,
            "importance": None,
            "value": None,
            "valuePeriod": None,
            "ranking": None,
            "dates": None,
            "isPinned": False,
            "createdUnix": 1,
            "updatedUnix": 2,
            "permissions": {"read": True, "write": False},
            "futureField": "preserved",
        }
    )

    assert document.blocks[0].type == "header"
    assert document.model_extra == {"futureField": "preserved"}


def test_snapshot_counts_parse() -> None:
    snapshot = SnapshotResponse.model_validate({"areas": [], "areaCount": 0, "documentCount": 0})

    assert snapshot.areaCount == 0
