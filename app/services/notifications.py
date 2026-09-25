"""Contrato de notificación y sus implementaciones (consola, pruebas, webhook)."""

from __future__ import annotations

from typing import Any, Protocol

from app.models.entities import Ticket


class Notifier(Protocol):
    """Contrato que deben cumplir todos los canales de notificación."""

    def notify(self, event: str, ticket: Ticket, **details: Any) -> None: ...


class ConsoleNotifier:
    """Implementación por defecto: imprime el evento en consola."""

    def notify(self, event: str, ticket: Ticket, **details: Any) -> None:
        print(f"[{event}] Ticket #{ticket.id} - {ticket.title} :: {details}")


class RecordingNotifier:
    """Implementación de pruebas: registra los eventos sin depender de stdout."""

    def __init__(self) -> None:
        self.sent: list[dict[str, Any]] = []

    def notify(self, event: str, ticket: Ticket, **details: Any) -> None:
        self.sent.append({"event": event, "ticket_id": ticket.id, **details})


class WebhookNotifier:
    """Simula el envío de notificaciones a un webhook externo.

    No realiza llamadas HTTP reales: guarda los payloads que hubiera enviado
    en ``sent_payloads`` para poder verificarlos en las pruebas.
    """

    def __init__(self, url: str) -> None:
        self.url = url
        self.sent_payloads: list[dict[str, Any]] = []

    def notify(self, event: str, ticket: Ticket, **details: Any) -> None:
        payload = {
            "url": self.url,
            "event": event,
            "ticket_id": ticket.id,
            **details,
        }
        self.sent_payloads.append(payload)
