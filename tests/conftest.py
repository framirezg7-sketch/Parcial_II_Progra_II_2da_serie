from __future__ import annotations

import pytest

from app.models.entities import Role
from app.repositories.memory import InMemoryTicketRepository, InMemoryUserRepository
from app.services.notifications import RecordingNotifier
from app.services.tickets import TicketService
from app.services.users import UserService


@pytest.fixture
def user_repository() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def user_service(user_repository: InMemoryUserRepository) -> UserService:
    return UserService(user_repository)


@pytest.fixture
def ticket_repository() -> InMemoryTicketRepository:
    return InMemoryTicketRepository()


@pytest.fixture
def notifier() -> RecordingNotifier:
    return RecordingNotifier()


@pytest.fixture
def ticket_service(
    ticket_repository: InMemoryTicketRepository,
    user_service: UserService,
    notifier: RecordingNotifier,
) -> TicketService:
    return TicketService(ticket_repository, user_service, notifier=notifier)


@pytest.fixture
def requester(user_service: UserService):
    return user_service.create("Ana Solicitante", "ana@helpdesk.edu", Role.REQUESTER)


@pytest.fixture
def technician(user_service: UserService):
    return user_service.create("Luis Tecnico", "luis@helpdesk.edu", Role.TECHNICIAN)


@pytest.fixture
def other_technician(user_service: UserService):
    return user_service.create("Marta Tecnica", "marta@helpdesk.edu", Role.TECHNICIAN)
