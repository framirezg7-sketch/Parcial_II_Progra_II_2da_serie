"""Servicio de aplicación para tickets: orquesta reglas de negocio,
persistencia (a través de TicketRepository) y notificaciones."""

from __future__ import annotations

from app.domain.errors import DuplicateAssignmentError, TicketNotFoundError
from app.models.entities import Comment, HistoryEvent, Ticket, TicketStatus, User
from app.repositories.base import TicketRepository
from app.services.notifications import ConsoleNotifier, Notifier
from app.services.users import UserService


class TicketService:
    def __init__(
        self,
        repository: TicketRepository,
        users: UserService,
        notifier: Notifier | None = None,
    ) -> None:
        self._repository = repository
        self._users = users
        self._notifier = notifier or ConsoleNotifier()

    def require(self, ticket_id: int) -> Ticket:
        """Devuelve el ticket o lanza TicketNotFoundError si no existe."""
        ticket = self._repository.by_id(ticket_id)
        if ticket is None:
            raise TicketNotFoundError(ticket_id)
        return ticket

    def create(self, title: str, description: str, requester_id: int) -> Ticket:
        self._users.require(requester_id)
        ticket = Ticket(
            id=self._repository.next_id(),
            title=title,
            description=description,
            status=TicketStatus.OPEN,
            requester_id=requester_id,
        )
        return self._repository.add(ticket)

    def assign(self, ticket_id: int, technician_id: int) -> Ticket:
        ticket = self.require(ticket_id)
        technician = self._users.require(technician_id)

        if ticket.assignee_id == technician_id:
            raise DuplicateAssignmentError(ticket_id, technician_id)

        ticket.assignee_id = technician_id
        ticket.status = TicketStatus.IN_PROGRESS
        ticket.history.append(
            HistoryEvent(
                id=len(ticket.history) + 1,
                ticket_id=ticket_id,
                description=f"Asignado a {technician.name}",
            )
        )
        self._repository.update(ticket)
        self._notifier.notify("ticket_assigned", ticket, technician_id=technician_id)
        return ticket

    def watchers(self, ticket_id: int) -> list[User]:
        """Devuelve el solicitante y, si existe, el técnico asignado,
        sin repetir usuarios con el mismo id."""
        ticket = self.require(ticket_id)

        result: list[User] = []
        seen_ids: set[int] = set()

        requester = self._users.require(ticket.requester_id)
        result.append(requester)
        seen_ids.add(requester.id)

        if ticket.assignee_id is not None:
            technician = self._users.require(ticket.assignee_id)
            if technician.id not in seen_ids:
                result.append(technician)
                seen_ids.add(technician.id)

        return result

    def add_comment(self, ticket_id: int, author_id: int, body: str) -> Ticket:
        ticket = self.require(ticket_id)
        self._users.require(author_id)
        ticket.comments.append(
            Comment(
                id=len(ticket.comments) + 1,
                ticket_id=ticket_id,
                author_id=author_id,
                body=body,
            )
        )
        self._repository.update(ticket)
        return ticket
