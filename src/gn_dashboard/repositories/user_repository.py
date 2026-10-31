"""Acesso a dados de utilizadores (tabela `AUTILIS`)."""

import logging
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from gn_dashboard.database.query_builder import QueryBuilder
from gn_dashboard.database.session import DatabaseManager, get_database_manager
from gn_dashboard.models.users import Users

logger = logging.getLogger(__name__)


class UserRepository:
    """Operações de base de dados relativas a utilizadores.

    Args:
        db: Gestor da base de dados; por omissão usa o partilhado pelo processo.
    """

    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db or get_database_manager()

    def get_by_username(self, username: str) -> Optional[Users]:
        """Obtém um utilizador pelo código (`USR_0`).

        Args:
            username: Código do utilizador (não distingue maiúsculas/minúsculas).

        Returns:
            O utilizador, ou `None` se não existir ou ocorrer um erro.
        """
        if not self.db:
            logger.error('Database connection is not established.')
            return None

        if not username:
            logger.error('Username is empty or None.')
            return None

        logger.info('Retrieving user by username: %s', username)
        try:
            with self.db.get_db() as session:
                stmt = select(Users).where(Users.username == username.upper())
                return session.execute(stmt).scalar_one_or_none()
        except Exception as e:  # noqa: BLE001
            logger.error('Error retrieving user by username %s: %s', username, e, exc_info=True)
        return None

    def set_user_password(self, user: Users, new_password_hash: str) -> bool:
        """Grava o hash da password do utilizador.

        Args:
            user: Utilizador a atualizar.
            new_password_hash: Novo hash da password.

        Returns:
            `True` se a gravação teve sucesso.
        """
        if not self.db:
            logger.error('Database connection is not established.')
            return False

        if not new_password_hash:
            logger.warning('Hash de password vazio; nada a atualizar.')
            return False

        user.password = new_password_hash
        logger.info('Attempting to set password for user: %s', user.username)
        try:
            with self.db.get_db() as session:
                if not self.update_control(db=session, user_data=user):
                    logger.warning('User %s not found for password update.', user.username)
                    return False
                logger.info('Password updated successfully for user: %s', user.username)
                return True
        except Exception as e:  # noqa: BLE001
            logger.error('Error updating password for user %s: %s', user.username, e, exc_info=True)
            return False

    @staticmethod
    def update_control(db: Session, user_data: Users) -> Users:
        """Faz merge e commit de um utilizador existente.

        Args:
            db: Sessão SQLAlchemy.
            user_data: Utilizador (possivelmente desligado da sessão).

        Returns:
            O objeto gerido pela sessão, já atualizado.
        """
        managed_obj = db.merge(user_data)
        db.flush()
        db.commit()
        db.refresh(managed_obj)
        return managed_obj

    def get_user_summary(self, username: str) -> dict[str, Any]:
        """Obtém um resumo do utilizador via SQL direto (sem ORM).

        Args:
            username: Código do utilizador.

        Returns:
            Dicionário com `id`, `username`, `name`, `login` e `password`, ou `{}` se não existir.
        """
        if not self.db or not username:
            return {}

        query = QueryBuilder(db_manager=self.db)
        result = query.execute_query(
            table=f'{query.schema}.AUTILIS',
            columns=['ROWID', 'USR_0', 'NOMUSR_0', 'LOGIN_0', 'YPWDHASH_0'],
            where_clauses={'USR_0': ('=', username.upper())},
            limit=1,
        )

        if result['status'] != 'success' or result['records'] == 0:
            logger.warning('Utilizador %s não encontrado.', username)
            return {}

        data = result['data'][0]
        return {
            'id': data['ROWID'],
            'username': data['USR_0'],
            'name': data['NOMUSR_0'],
            'login': data['LOGIN_0'],
            'password': data['YPWDHASH_0'],
        }
