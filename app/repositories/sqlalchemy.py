"""Modelos ORM y repositorio SQLAlchemy para tickets.

La capa de dominio (app.models.entities) nunca se expone a SQLAlchemy: este
módulo traduce entre filas ORM y dataclasses de dominio para que TicketService
no dependa de detalles de persistencia.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

from app.models.entities import Comment, HistoryEvent, Ticket, TicketStatus
from app.repositories.base import TicketRepository


class Base(DeclarativeBase):
    pass


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(160), unique=True)
    role: Mapped[str] = mapped_column(String(20))


class TicketORM(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default=TicketStatus.OPEN.value)
    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    # foreign_keys es obligatorio aquí: hay dos FK hacia users.id
    # (requester_id y assignee_id) y SQLAlchemy no puede inferir sola
    # a cuál columna corresponde cada relationship.
    requester = relationship("UserORM", foreign_keys=[requester_id])
    assignee = relationship("UserORM", foreign_keys=[assignee_id])

    comments: Mapped[list["CommentORM"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan"
    )
    history: Mapped[list["HistoryEventORM"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan"
    )


class CommentORM(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now().astimezone()
    )

    ticket = relationship("TicketORM", back_populates="comments")


class HistoryEventORM(Base):
    __tablename__ = "ticket_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"))
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now().astimezone()
    )

    ticket = relationship("TicketORM", back_populates="history")


def _ticket_to_domain(row: TicketORM) -> Ticket:
    """Construye un Ticket (dataclass) a partir de una fila ORM.

    Se hace explícitamente en vez de devolver `row` para que TicketService
    no tenga que conocer detalles de SQLAlchemy (Session, lazy loading,
    identidad de fila, etc.), manteniendo separadas las capas de dominio
    y de persistencia.
    """
    ticket = Ticket(
        id=row.id,
        title=row.title,
        description=row.description,
        status=TicketStatus(row.status),
        requester_id=row.requester_id,
        assignee_id=row.assignee_id,
    )
    ticket.comments = [
        Comment(
            id=c.id,
            ticket_id=c.ticket_id,
            author_id=c.author_id,
            body=c.body,
            created_at=c.created_at,
        )
        for c in row.comments
    ]
    ticket.history = [
        HistoryEvent(
            id=h.id,
            ticket_id=h.ticket_id,
            description=h.description,
            created_at=h.created_at,
        )
        for h in row.history
    ]
    return ticket


class SqlAlchemyTicketRepository(TicketRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, ticket: Ticket) -> Ticket:
        row = TicketORM(
            title=ticket.title,
            description=ticket.description,
            status=ticket.status.value,
            requester_id=ticket.requester_id,
            assignee_id=ticket.assignee_id,
        )
        self._session.add(row)
        self._session.flush()
        return _ticket_to_domain(row)

    def by_id(self, ticket_id: int) -> Ticket | None:
        row = self._session.get(TicketORM, ticket_id)
        return _ticket_to_domain(row) if row is not None else None

    def list(
        self,
        *,
        status: TicketStatus | None = None,
        assignee_id: int | None = None,
        requester_id: int | None = None,
    ) -> list[Ticket]:
        stmt = select(TicketORM)
        if status is not None:
            stmt = stmt.where(TicketORM.status == status.value)
        if assignee_id is not None:
            stmt = stmt.where(TicketORM.assignee_id == assignee_id)
        if requester_id is not None:
            stmt = stmt.where(TicketORM.requester_id == requester_id)
        rows = self._session.execute(stmt).scalars().all()
        return [_ticket_to_domain(row) for row in rows]

    def next_id(self) -> int:
        """No aplica de forma estricta en SQL (el id lo asigna la base de
        datos al insertar), pero se implementa para cumplir el contrato
        TicketRepository y permitir previsualizar el próximo id disponible.
        """
        max_id = self._session.execute(select(func.max(TicketORM.id))).scalar()
        return (max_id or 0) + 1

    def update(self, ticket: Ticket) -> None:
        row = self._session.get(TicketORM, ticket.id)
        if row is None:
            raise ValueError(f"No existe el ticket {ticket.id} para actualizar")
        row.title = ticket.title
        row.description = ticket.description
        row.status = ticket.status.value
        row.assignee_id = ticket.assignee_id
        self._session.flush()

    def count_by_status(self) -> dict[str, int]:
        """Reporte agregado: cantidad de tickets por estado.

        Devuelve únicamente los estados presentes en la base de datos y un
        diccionario vacío si no hay tickets. No forma parte de la interfaz
        abstracta TicketRepository.
        """
        rows = self._session.execute(
            select(TicketORM.status, func.count()).group_by(TicketORM.status)
        ).all()
        return {status: count for status, count in rows}
