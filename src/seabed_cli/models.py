from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

DocumentKind = Literal["folder", "note", "context", "spec", "runbook", "decision", "source"]
DocumentIcon = Literal[
    "file-text",
    "folder",
    "book-open",
    "lightbulb",
    "flask-conical",
    "rocket",
    "clipboard-list",
    "database",
    "heart",
    "star",
    "code-2",
    "briefcase",
]
DocumentColor = Literal["sky", "coral", "amber", "emerald", "violet", "rose", "slate"]
DocumentStatus = Literal["not-started", "in-progress", "blocked", "completed", "cancelled"]
DocumentImportance = Literal["low", "medium", "high", "critical"]
ValuePeriod = Literal["one-time", "weekly", "fortnightly", "monthly", "quarterly", "annually"]


class SeabedModel(BaseModel):
    """A forward-compatible public API model."""

    model_config = ConfigDict(extra="allow")


class Permissions(SeabedModel):
    read: bool
    write: bool


class Area(SeabedModel):
    id: str
    name: str
    slug: str
    description: str | None
    isDefault: bool
    createdUnix: float
    updatedUnix: float
    permissions: Permissions


class AreaListResponse(SeabedModel):
    areas: list[Area]
    count: int


class BlockBase(SeabedModel):
    id: str


class HeaderBlock(BlockBase):
    type: Literal["header"]
    level: Literal[1, 2, 3]
    text: str


class TextBlock(BlockBase):
    type: Literal["text"]
    text: str
    formatting: list[Any]


class ParagraphBlock(BlockBase):
    type: Literal["paragraph"]
    text: str
    formatting: list[Any]


class ImageBlock(BlockBase):
    type: Literal["image"]
    url: str
    alt: str | None = None
    caption: str | None = None
    width: int | None = None
    height: int | None = None


class AttachmentBlock(BlockBase):
    type: Literal["attachment"]
    url: str
    fileName: str
    mimeType: str
    size: int
    caption: str | None = None


class LinkBlock(BlockBase):
    type: Literal["link"]
    href: str
    text: str
    isInternal: bool


class DiagramViewport(SeabedModel):
    x: float = 0
    y: float = 0
    zoom: float = 1


class DiagramBlock(BlockBase):
    type: Literal["diagram"]
    title: str | None = None
    diagramType: str = "flowchart"
    nodes: list[Any] = Field(default_factory=list)
    edges: list[Any] = Field(default_factory=list)
    viewport: DiagramViewport = Field(default_factory=DiagramViewport)


Block = Annotated[
    HeaderBlock | TextBlock | ParagraphBlock | ImageBlock | AttachmentBlock | LinkBlock | DiagramBlock,
    Field(discriminator="type"),
]


class DocumentDates(SeabedModel):
    dueDateUnix: float | None = None
    fromDateUnix: float | None = None
    uptoDateUnix: float | None = None
    reviewDateUnix: float | None = None
    completedDateUnix: float | None = None
    customDates: dict[str, float] | None = None


class Document(SeabedModel):
    id: str
    areaId: str
    title: str
    body: str
    kind: DocumentKind
    parentDocumentId: str | None
    path: list[str]
    depth: int
    sortOrder: int
    tags: list[str]
    sourceUrl: str | None
    summary: str | None
    icon: DocumentIcon | None
    color: DocumentColor | None
    blocks: list[Block]
    status: DocumentStatus | None
    importance: DocumentImportance | None
    value: float | None
    valuePeriod: ValuePeriod | None
    ranking: int | None
    dates: DocumentDates | None
    isPinned: bool
    createdUnix: float
    updatedUnix: float
    permissions: Permissions


class DocumentListResponse(SeabedModel):
    documents: list[Document]
    count: int


class AreaSnapshot(SeabedModel):
    area: Area
    documents: list[Document]


class SnapshotResponse(SeabedModel):
    areas: list[AreaSnapshot]
    areaCount: int
    documentCount: int


class AppendBlocksResponse(SeabedModel):
    document: Document
    appendedCount: int
    blockIds: list[str]


class DeleteResponse(SeabedModel):
    deleted: bool
    documentId: str
