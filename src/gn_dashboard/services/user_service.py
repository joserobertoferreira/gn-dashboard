"""Operações de alto nível sobre utilizadores.

Substitui a versão anterior, que dependia de módulos inexistentes
(`database.manager`, modelos Pydantic `User`/`UserUpdate`) e não podia ser importada.
"""

import logging
from typing import Any, Optional

from gn_dashboard.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class UserService:
    """Serviço de gestão de utilizadores.

    Args:
        repository: Repositório de utilizadores (injetável para testes).
    """

    def __init__(self, repository: Optional[UserRepository] = None):
        self.repository = repository or UserRepository()

    def get_user(self, username: str) -> dict[str, Any]:
        """Devolve os dados públicos de um utilizador.

        Args:
            username: Código do utilizador.

        Returns:
            Dicionário com `id`, `name`, `username`, `login` e `email`, ou `{}` se não existir.
        """
        user = self.repository.get_by_username(username)
        if not user:
            return {}
        return user.to_dict(include=('id', 'name', 'username', 'login', 'email'))

    def set_password_hash(self, username: str, password_hash: str) -> bool:
        """Grava um novo hash de password para o utilizador.

        Args:
            username: Código do utilizador.
            password_hash: Hash já calculado (ver `AuthenticationService.hash_password`).

        Returns:
            `True` se a gravação teve sucesso.
        """
        user = self.repository.get_by_username(username)
        if not user:
            logger.warning('Utilizador %s não encontrado.', username)
            return False
        return self.repository.set_user_password(user, password_hash)
