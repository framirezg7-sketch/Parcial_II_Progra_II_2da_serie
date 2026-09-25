"""Ejercicio 2: Observadores y relaciones entre objetos (TicketService.watchers)."""

from __future__ import annotations

import pytest

from app.domain.errors import TicketNotFoundError
from app.services.tickets import TicketService


def test_watchers_without_technician(ticket_service: TicketService, requester):
    ticket = ticket_service.create("Sin red", "No hay conexión", requester.id)

    watchers = ticket_service.watchers(ticket.id)

    assert watchers == [requester]


def test_watchers_with_distinct_technician(
    ticket_service: TicketService, requester, technician
):
    ticket = ticket_service.create("Sin red", "No hay conexión", requester.id)
    ticket_service.assign(ticket.id, technician.id)

    watchers = ticket_service.watchers(ticket.id)

    assert watchers == [requester, technician]


def test_watchers_propagates_ticket_not_found(ticket_service: TicketService):
    with pytest.raises(TicketNotFoundError):
        ticket_service.watchers(999)


def test_watchers_deduplicates_same_user_as_requester_and_assignee(
    ticket_service: TicketService, ticket_repository, requester
):
    ticket = ticket_service.create("Autoservicio", "El solicitante se autoasigna", requester.id)

    # El dominio no prohíbe que el propio solicitante quede como técnico
    # asignado; se fuerza ese escenario controlado para probar la
    # deduplicación de watchers() sin pasar por assign() (que sí podría
    # tener reglas propias de reasignación).
    stored_ticket = ticket_repository.by_id(ticket.id)
    stored_ticket.assignee_id = requester.id
    ticket_repository.update(stored_ticket)

    watchers = ticket_service.watchers(ticket.id)

    assert watchers == [requester]
