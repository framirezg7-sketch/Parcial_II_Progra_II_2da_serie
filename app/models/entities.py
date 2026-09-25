"""Entidades de dominio (dataclasses) del proyecto HelpDesk EDU."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from app.domain.errors import ValidationError


class Role(StrEnum):
    REQUESTER = "requester"
    TECHNICIAN = "technician"
    ADMIN = "admin"


class TicketStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


@dataclass
class User:
    id: int
    name: str
    email: str
    role: Role


@dataclass
class Comment:
    id: int
    ticket_id: int
    author_id: int
    body: str
    created_at: datetime = field(default_factory=lambda: datetime.now().astimezone())


@dataclass
class HistoryEvent:
    id: int
    ticket_id: int
    description: str
    created_at: datetime = field(default_factory=lambda: datetime.now().astimezone())


@dataclass
class Ticket:
    id: int
    title: str
    description: str
    status: TicketStatus
    requester_id: int
    assignee_id: int | None = None
    comments: list[Comment] = field(default_factory=list)
    history: list[HistoryEvent] = field(default_factory=list)
    _tags: list[str] = field(default_factory=list, init=False, repr=False)

    @property
    def tags(self) -> tuple[str, ...]:
        """Vista de solo lectura de las etiquetas del ticket."""
        return tuple(self._tags)

    def add_tag(self, tag: str) -> None:
        """Normaliza, valida y agrega una etiqueta evitando duplicados."""
        normalized = tag.strip().lower()
        if not normalized:
            raise ValidationError("La etiqueta no puede estar vacía")
        if normalized not in self._tags:
            self._tags.append(normalized)
