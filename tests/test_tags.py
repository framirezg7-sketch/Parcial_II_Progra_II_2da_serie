"""Ejercicio 1: Etiquetas y encapsulamiento."""

from __future__ import annotations

import pytest

from app.domain.errors import ValidationError
from app.models.entities import Ticket, TicketStatus


def make_ticket(ticket_id: int = 1) -> Ticket:
    return Ticket(
        id=ticket_id,
        title="Impresora no enciende",
        description="La impresora del segundo piso no enciende",
        status=TicketStatus.OPEN,
        requester_id=1,
    )


def test_add_tag_normalizes_and_rejects_duplicates():
    ticket = make_ticket()

    ticket.add_tag("  Hardware ")
    ticket.add_tag("hardware")  # ya existe normalizado, no debe duplicarse
    ticket.add_tag("URGENTE")

    assert ticket.tags == ("hardware", "urgente")


def test_add_tag_rejects_blank_values():
    ticket = make_ticket()

    with pytest.raises(ValidationError):
        ticket.add_tag("   ")

    with pytest.raises(ValidationError):
        ticket.add_tag("")

    assert ticket.tags == ()


def test_tags_are_independent_between_instances():
    ticket_a = make_ticket(1)
    ticket_b = make_ticket(2)

    ticket_a.add_tag("hardware")

    assert ticket_a.tags == ("hardware",)
    assert ticket_b.tags == ()


def test_tags_property_cannot_be_reassigned():
    ticket = make_ticket()

    with pytest.raises(AttributeError):
        ticket.tags = ("hack",)  # type: ignore[misc]
