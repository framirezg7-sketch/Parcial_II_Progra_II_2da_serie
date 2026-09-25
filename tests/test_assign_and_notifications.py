"""Ejercicio 3: Excepciones y polimorfismo (DuplicateAssignmentError, WebhookNotifier)."""

from __future__ import annotations

import pytest

from app.domain.errors import DuplicateAssignmentError
from app.services.notifications import WebhookNotifier
from app.services.tickets import TicketService
from app.services.users import UserService


def test_duplicate_assignment_raises_without_side_effects(
    ticket_service: TicketService, notifier, requester, technician
):
    ticket = ticket_service.create("Teclado defectuoso", "No responden las teclas", requester.id)
    ticket_service.assign(ticket.id, technician.id)

    history_before = list(ticket.history)
    notifications_before = list(notifier.sent)

    with pytest.raises(DuplicateAssignmentError):
        ticket_service.assign(ticket.id, technician.id)

    assert ticket.history == history_before
    assert notifier.sent == notifications_before


def test_valid_assignment_still_works_after_rejected_duplicate(
    ticket_service: TicketService, requester, technician, other_technician
):
    ticket = ticket_service.create("Monitor parpadea", "Pantalla intermitente", requester.id)
    ticket_service.assign(ticket.id, technician.id)

    with pytest.raises(DuplicateAssignmentError):
        ticket_service.assign(ticket.id, technician.id)

    # Reasignar a un técnico distinto sigue siendo una operación válida.
    updated = ticket_service.assign(ticket.id, other_technician.id)
    assert updated.assignee_id == other_technician.id


def test_webhook_notifier_receives_payload_on_valid_assign(
    ticket_repository, user_service: UserService, requester, technician
):
    webhook = WebhookNotifier(url="https://example.org/hooks/helpdesk")
    service = TicketService(ticket_repository, user_service, notifier=webhook)

    ticket = service.create("VPN caída", "No conecta la VPN", requester.id)
    service.assign(ticket.id, technician.id)

    assert len(webhook.sent_payloads) == 1
    payload = webhook.sent_payloads[0]
    assert payload["event"] == "ticket_assigned"
    assert payload["ticket_id"] == ticket.id
    assert payload["technician_id"] == technician.id
    assert payload["url"] == "https://example.org/hooks/helpdesk"
