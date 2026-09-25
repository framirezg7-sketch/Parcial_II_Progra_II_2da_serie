"""Contratos (interfaces) de repositorio para HelpDesk EDU."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.entities import Ticket, TicketStatus, User


class TicketRepository(ABC):
    """Puerto de persistencia para tickets. Las implementaciones concretas
    (memoria, SQLAlchemy, etc.) deben cumplir este contrato."""

    @abstractmethod
    def add(self, ticket: Ticket) -> Ticket: ...

    @abstractmethod
    def by_id(self, ticket_id: int) -> Ticket | None: ...

    @abstractmethod
    def list(
        self,
        *,
        status: TicketStatus | None = None,
        assignee_id: int | None = None,
        requester_id: int | None = None,
    ) -> list[Ticket]: ...

    @abstractmethod
    def next_id(self) -> int: ...

    @abstractmethod
    def update(self, ticket: Ticket) -> None: ...


class UserRepository(ABC):
    """Puerto de persistencia para usuarios."""

    @abstractmethod
    def add(self, user: User) -> User: ...

    @abstractmethod
    def by_id(self, user_id: int) -> User | None: ...

    @abstractmethod
    def list(self) -> list[User]: ...

    @abstractmethod
    def next_id(self) -> int: ...
