"""Ejercicio 5: Consulta agregada y persistencia con SQLAlchemy (count_by_status)."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.entities import Role, Ticket, TicketStatus
from app.repositories.sqlalchemy import Base, SqlAlchemyTicketRepository, UserORM


@pytest.fixture
def engine():
    # StaticPool + sqlite:// en memoria: todas las sesiones de la prueba
    # comparten la misma conexión y por lo tanto ven las mismas tablas.
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def session_factory(engine):
    return sessionmaker(bind=engine)


def _seed_user(session: Session) -> UserORM:
    user = UserORM(name="Ana", email="ana@helpdesk.edu", role=Role.REQUESTER.value)
    session.add(user)
    session.flush()
    return user


def test_count_by_status_full_dict_after_commit_in_new_session(session_factory):
    with session_factory() as write_session:
        requester = _seed_user(write_session)
        repo = SqlAlchemyTicketRepository(write_session)

        repo.add(
            Ticket(
                id=0,
                title="Ticket 1",
                description="desc",
                status=TicketStatus.OPEN,
                requester_id=requester.id,
            )
        )
        repo.add(
            Ticket(
                id=0,
                title="Ticket 2",
                description="desc",
                status=TicketStatus.OPEN,
                requester_id=requester.id,
            )
        )
        repo.add(
            Ticket(
                id=0,
                title="Ticket 3",
                description="desc",
                status=TicketStatus.IN_PROGRESS,
                requester_id=requester.id,
            )
        )
        write_session.commit()

    # Sesión completamente nueva sobre el mismo engine/StaticPool: si los
    # datos aparecen aquí es porque quedaron persistidos, no porque se
    # esté leyendo el mismo objeto en memoria de la sesión anterior.
    with session_factory() as read_session:
        report = SqlAlchemyTicketRepository(read_session).count_by_status()

    assert report == {
        TicketStatus.OPEN.value: 2,
        TicketStatus.IN_PROGRESS.value: 1,
    }
    assert sum(report.values()) == 3


def test_count_by_status_empty_database_returns_empty_dict(session_factory):
    with session_factory() as session:
        report = SqlAlchemyTicketRepository(session).count_by_status()

    assert report == {}
