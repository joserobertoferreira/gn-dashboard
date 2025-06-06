import logging
from typing import Any, Optional

import streamlit as st
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.database import db
from database.database_core import DatabaseCoreManager
from models.users import Users

logger = logging.getLogger(__name__)


class UserRepository:
    """
    Repository for user-related database operations.
    """

    def __init__(self):
        self.db = db

    def get_by_username(self, username: str) -> Optional[Users]:
        """
        Retrieves user information by username.
        :param username: Username of the user
        :return: A dictionary containing user information if found, otherwise an empty dictionary
        """
        logger.info(f'Retrieving user by username: {username}')

        if not self.db:
            logger.error('Database connection is not established.')
            return None

        if not username:
            logger.error('Username is empty or None.')
            return None

        logger.info('Database connection established. Retrieve data...')

        try:
            with self.db.get_db() as session:
                stmt = select(Users).where(Users.username == username.upper())

                user = session.execute(stmt).scalar_one_or_none()

                return user
        except Exception as e:
            logger.error(f'Error retrieving user by username {username}: {e}', exc_info=True)

        return None

    def set_user_password(self, user: Users, new_password_hash: str) -> bool:
        """
        Sets or updates the user's password hash in the database.
        :param user_id: ID of the user.
        :param new_password_hash: The new hashed password.
        :return: True if successful, False otherwise.
        """
        if not self.db:
            logger.error('Database connection is not established.')
            st.error('Gerenciador do banco não disponível.')
            return False

        if not new_password_hash:
            logger.warning('Nenhuma cláusula SET gerada para a query de atualização.')
            return False

        user.password = new_password_hash

        logger.info(f'Attempting to set password for user_id: {user.username}')
        try:
            with self.db.get_db() as session:
                update_user = self.update_control(db=session, user_data=user)

                if not update_user:
                    logger.warning(f'User with ID {user.username} not found for password update.')
                    return False

                logger.info(f'Password updated successfully for user: {user.username}')
                return True
        except Exception as e:
            logger.error(f'Error retrieving user by username {user.username}: {e}', exc_info=True)
            return False

    @staticmethod
    def update_control(db: Session, user_data: Users) -> Users:
        """Update an existing user in the database."""

        managed_obj = db.merge(user_data)

        db.flush()
        db.commit()
        db.refresh(managed_obj)

        return managed_obj

    def get_by_username_(self, username: str) -> dict[str, Any]:
        db_core = DatabaseCoreManager(db_manager=self.db)

        print(db_core.schema)

        result = db_core.execute_query(
            table=f'{db_core.schema}.AUTILIS',
            columns=['ROWID', 'USR_0', 'NOMUSR_0', 'LOGIN_0', 'YPWDHASH_0'],
            where_clauses={'USR_0': ('=', username.upper())},
            limit=1,
        )

        print(f'Query result: {result}')

        if result is None:
            logger.error('Erro ao consultar o banco de dados. Verifique os logs para mais detalhes.')
            return {}

        if result['records'] == 0:
            logger.warning('Nenhuma empresa encontrada no banco de dados.')
            return {}

        data = result['data'][0]

        user = {
            'id': data['ROWID'],
            'username': data['USR_0'],
            'name': data['NOMUSR_0'],
            'login': data['LOGIN_0'],
            'password': data['YPWDHASH_0'],
        }

        return user
