"""Servicio de aplicación para usuarios."""

from __future__ import annotations

from app.domain.errors import UserNotFoundError
from app.models.entities import Role, User
from app.repositories.base import UserRepository


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def require(self, user_id: int) -> User:
        """Devuelve el usuario o lanza UserNotFoundError si no existe."""
        user = self._repository.by_id(user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        return user

    def create(self, name: str, email: str, role: Role) -> User:
        user = User(id=self._repository.next_id(), name=name, email=email, role=role)
        return self._repository.add(user)

    def list(self) -> list[User]:
        return self._repository.list()
