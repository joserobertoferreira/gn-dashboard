"""Autenticação de utilizadores com hashes Argon2 (via `pwdlib`)."""

import logging
from typing import Any

from pwdlib import PasswordHash

from gn_dashboard.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

#: Campos do utilizador devolvidos após autenticação bem-sucedida.
PUBLIC_USER_FIELDS = ('id', 'name', 'username')


class AuthenticationService:
    """Serviço de autenticação de utilizadores."""

    #: Contexto de hashing de passwords (Argon2).
    pwd_context = PasswordHash.recommended()

    @staticmethod
    def hash_password(password: str) -> str:
        """Gera o hash de uma password."""
        return AuthenticationService.pwd_context.hash(password)

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verifica uma password contra o respetivo hash."""
        try:
            return AuthenticationService.pwd_context.verify(password, password_hash)
        except Exception as e:  # noqa: BLE001 - hash inválido / formato desconhecido
            logger.warning('Não foi possível verificar a password: %s', e)
            return False

    @staticmethod
    def login(username: str, password: str) -> dict[str, Any]:
        """Autentica um utilizador.

        Se o utilizador ainda não tiver password definida (`YPWDHASH_0` vazio),
        a password indicada é gravada como a sua password (primeiro acesso).

        Args:
            username: Código do utilizador.
            password: Password em texto simples.

        Returns:
            Dicionário com `id`, `name` e `username` se a autenticação tiver sucesso, ou `{}`.
        """
        if not username or not password:
            return {}

        user_repository = UserRepository()
        user = user_repository.get_by_username(username=username)

        if not user:
            logger.warning('User %s not found during login attempt.', username)
            return {}

        logger.info('User %s found in database.', user.username)
        db_password = str(user.password or '').strip()

        if not db_password:
            logger.warning('User %s has no password set. Setting it on first login.', username)
            if user_repository.set_user_password(user, new_password_hash=AuthenticationService.hash_password(password)):
                logger.info('Password set for user %s.', username)
                return user.to_dict(include=PUBLIC_USER_FIELDS)
            logger.error('Failed to set password for user %s.', username)
            return {}

        if AuthenticationService.verify_password(password, db_password):
            return user.to_dict(include=PUBLIC_USER_FIELDS)

        return {}

    @staticmethod
    def change_password(username: str, current_password: str, new_password: str) -> bool:
        """Altera a password de um utilizador, validando a password atual.

        Args:
            username: Código do utilizador.
            current_password: Password atual.
            new_password: Nova password.

        Returns:
            `True` se a password foi alterada.
        """
        if not new_password:
            return False

        user_repository = UserRepository()
        user = user_repository.get_by_username(username=username)
        if not user:
            return False

        db_password = str(user.password or '').strip()
        if db_password and not AuthenticationService.verify_password(current_password, db_password):
            logger.warning('Password atual incorreta para o utilizador %s.', username)
            return False

        return user_repository.set_user_password(user, AuthenticationService.hash_password(new_password))
