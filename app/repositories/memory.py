"""Implementaciones en memoria de los repositorios (usadas en pruebas y demos)."""

from __future__ import annotations

from app.models.entities import Ticket, TicketStatus, User
from app.repositories.base import TicketRepository, UserRepository


class InMemoryTicketRepository(TicketRepository):
    def __init__(self) -> None:
        self._tickets: dict[int, Ticket] = {}
        self._sequence = 0

    def add(self, ticket: Ticket) -> Ticket:
        self._tickets[ticket.id] = ticket
        return ticket

    def by_id(self, ticket_id: int) -> Ticket | None:
        return self._tickets.get(ticket_id)

    def list(
        self,
        *,
        status: TicketStatus | None = None,
        assignee_id: int | None = None,
        requester_id: int | None = None,
    ) -> list[Ticket]:
        results = list(self._tickets.values())
        if status is not None:
            results = [t for t in results if t.status == status]
        if assignee_id is not None:
            results = [t for t in results if t.assignee_id == assignee_id]
        if requester_id is not None:
            results = [t for t in results if t.requester_id == requester_id]
        return results

    def next_id(self) -> int:
        self._sequence += 1
        return self._sequence

    def update(self, ticket: Ticket) -> None:
        self._tickets[ticket.id] = ticket


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._users: dict[int, User] = {}
        self._sequence = 0

    def add(self, user: User) -> User:
        self._users[user.id] = user
        return user

    def by_id(self, user_id: int) -> User | None:
        return self._users.get(user_id)

    def list(self) -> list[User]:
        return list(self._users.values())

    def next_id(self) -> int:
        self._sequence += 1
        return self._sequence
