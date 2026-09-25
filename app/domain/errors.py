"""Jerarquía de excepciones de dominio para HelpDesk EDU."""

from __future__ import annotations


class DomainError(Exception):
    """Excepción base para todos los errores del dominio HelpDesk."""


class NotFoundError(DomainError):
    """Un recurso solicitado no existe."""


class TicketNotFoundError(NotFoundError):
    def __init__(self, ticket_id: int) -> None:
        super().__init__(f"Ticket {ticket_id} no encontrado")
        self.ticket_id = ticket_id


class UserNotFoundError(NotFoundError):
    def __init__(self, user_id: int) -> None:
        super().__init__(f"Usuario {user_id} no encontrado")
        self.user_id = user_id


class ValidationError(DomainError):
    """Los datos suministrados no cumplen las reglas del dominio."""


class InvalidTransitionError(DomainError):
    """Se intentó una transición de estado no permitida para un ticket."""


class DuplicateAssignmentError(DomainError):
    """Se intentó asignar un ticket al técnico que ya lo tiene asignado."""

    def __init__(self, ticket_id: int, technician_id: int) -> None:
        super().__init__(
            f"El ticket {ticket_id} ya está asignado al técnico {technician_id}"
        )
        self.ticket_id = ticket_id
        self.technician_id = technician_id
