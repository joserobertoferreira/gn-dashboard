import logging
from typing import Optional

import pyodbc
import streamlit as st
from pydantic import ValidationError

from database.manager import db
from models.users import User, UserUpdate
from utils.generics import Generics

logger = logging.getLogger(__name__)


class UserService:
    """
    Service class for managing users.
    """

    def __init__(self):
        pass

    @staticmethod
    def update(user_id: int, user_data: UserUpdate) -> None:  # noqa: PLR0911
        """
        Update user data in the database.
        :param user_id: ID of the user to update
        :param user_data_changes: Dictionary of {column_name: value} to update
        """

        if not db:
            st.error('Gerenciador do banco não disponível.')
            logger.error('Database manager not available for user update.')
            return

        if not user_data:
            logger.warning('No data provided for update.')
            return

        update_data = user_data.model_dump(by_alias=True, exclude_unset=True)

        if not update_data:
            logger.info('Nenhum campo válido fornecido para atualização após processar o payload.')
            st.warning('Nenhum dado válido fornecido para atualização.')
            return

        table_name = 'AUTILIS'
        id_column_name = 'ROWID'

        set_clauses = []
        params_list = []

        for column_name, value in update_data.items():
            set_clauses.append(f'{column_name} = ?')
            params_list.append(value)

        if not set_clauses:
            logger.warning('Nenhuma cláusula SET gerada para a query de atualização.')
            return

        params_list.append(user_id)

        query = f'UPDATE {table_name} SET {", ".join(set_clauses)} WHERE {id_column_name} = ?;'

        logger.info(f'(Service) Atualizar usuário ROWID {user_id} com query: "{query}" e params: {tuple(params_list)}')

        try:
            with db.get_db() as conn:
                cursor = conn.cursor()
                # Removido o log aqui porque já logamos a query completa acima
                # if db.log_queries:
                #     logger.info(f"Executando query pyodbc: {query} com params: {tuple(params_list)}")
                cursor.execute(query, tuple(params_list))

                if cursor.rowcount == 0:
                    logger.warning(f'Utilizador com ROWID {user_id} não encontrado ou nenhuma alteração feita.')
                    return

                logger.info(f'Utilizador ROWID {user_id} atualizado com sucesso. Linhas afetadas: {cursor.rowcount}')
                return
        except pyodbc.Error as e:
            st.error(f'Erro de banco de dados (PyODBC) ao atualizar utilizador ROWID {user_id}: {e}')
            logger.error(f'Erro PyODBC ao atualizar utilizador ROWID {user_id}: {e}', exc_info=True)
            return
        except Exception as e:
            st.error(f'Erro inesperado (PyODBC) ao atualizar utilizador ROWID {user_id}: {e}')
            logger.error(f'Erro inesperado PyODBC ao atualizar utilizador ROWID {user_id}: {e}', exc_info=True)
            return

    @staticmethod
    def set_user_password(schema: str, user_id: int, new_password_hash: str) -> bool:
        """
        Sets or updates the user's password hash in the database.
        :param user_id: ID of the user.
        :param new_password_hash: The new hashed password.
        :return: True if successful, False otherwise.
        """
        if not db:
            st.error('Gerenciador do banco não disponível.')
            logger.error('Database manager not available for user update.')
            return False

        if not new_password_hash:
            logger.warning('Nenhuma cláusula SET gerada para a query de atualização.')
            return False

        set_clauses = ['"ZPWDHASH_0" = ?']
        params = [new_password_hash, user_id]

        query = f'UPDATE "{schema}"."AUTILIS" SET {", ".join(set_clauses)} WHERE ROWID = ?;'

        logger.info(f'Attempting to set password for user_id: {user_id}')
        try:
            with db.get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(query, tuple(params))

                if cursor.rowcount == 0:
                    logger.warning(f'User with ID {user_id} not found for password update.')
                    return False

                logger.info(f'Password updated successfully for user_id: {user_id}')
                logger.info(f'User with ID {user_id} update successfully. Rows affected: {cursor.rowcount}')
                return True
        except pyodbc.Error as e:
            st.error(f'Erro de banco de dados (PyODBC) ao atualizar utilizador ROWID {user_id}: {e}')
            logger.error(f'Erro PyODBC ao atualizar utilizador ROWID {user_id}: {e}', exc_info=True)
            return False
        except Exception as e:
            st.error(f'Erro inesperado (PyODBC) ao atualizar utilizador ROWID {user_id}: {e}')
            logger.error(f'Erro inesperado PyODBC ao atualizar utilizador ROWID {user_id}: {e}', exc_info=True)
            return False

    @staticmethod
    def _conditions_to_username_email(
        username: Optional[str] = None, email: Optional[str] = None
    ) -> tuple[list[str], list[str]]:
        """
        Helper method to build conditions for querying users by username or email.
        Returns a tuple of conditions and parameters.
        """
        conditions = []
        params_list = []

        conditions.append('ENAFLG_0 = 2')  # Only active users

        if username is not None and email is not None:
            conditions.append('USR_0 = ? AND ADDEML_0 = ?')
            params_list.extend([username.upper(), email])
        elif username is not None:
            conditions.append('USR_0 = ?')
            params_list.append(username.upper())
        elif email is not None:
            conditions.append('ADDEML_0 = ?')
            params_list.append(email)

        return conditions, params_list

    def get_by_username_email(  # noqa: PLR0911
        self, schema: str, username: Optional[str] = None, email: Optional[str] = None
    ) -> Optional[User]:
        """
        Fetches a user by their username or email from the specified schema.
        Returns a User object if found, otherwise None.
        """

        if not db:
            st.error('Gerenciador do banco não disponível.')
            return None

        logger.info(f'(Service) Buscar utilizador por username: {username} ou email: {email}')

        if not username and not email:
            logger.warning('Nem username nem email foram fornecidos para buscar o utilizador.')
            return None

        select_columns = ['ROWID', 'NOMUSR_0', 'USR_0', 'LOGIN_0', 'ZPWDHASH_0', 'ADDEML_0']
        columns = ', '.join([f'"{col}"' for col in select_columns])
        base_query = f'SELECT {columns} FROM "{schema}"."AUTILIS"'

        conditions, params_list = self._conditions_to_username_email(username, email)

        if not conditions:
            logger.warning('Nenhuma condição válida foi gerada para a consulta de busca do utilizador.')
            return None

        query = f'{base_query} WHERE {" AND ".join(conditions)};'
        params = tuple(params_list)

        try:
            with db.get_db() as conn:
                cursor = conn.cursor()
                logger.info(f'Executing query: {query} with params: {params}')
                cursor.execute(query, params)

                result = cursor.fetchone()

                if result is None:
                    logger.warning(f'No user found for username: {username} or email: {email}')
                    return None

                user_data_dict = Generics.result_to_dict(cursor, result)
                if not user_data_dict:  # Verificação de segurança
                    logger.error('Generics.return_to_dict retornou None para uma linha não nula.')
                    return None

                try:
                    user_model = User(**user_data_dict)
                    logger.info(f'Utilizador encontrado e validado: {user_model.username} (ROWID: {user_model.id})')
                    return user_model
                except ValidationError as ve:
                    logger.error(f'Erro de validação Pydantic para dados do utilizador: {ve}', exc_info=True)
                    st.error(f'Os dados do utilizador recuperados são inválidos: {ve}')
                    return None
        except pyodbc.Error as e:
            st.error(f'Erro de banco de dados (PyODBC) ao buscar utilizador: {e}')
            logger.error(f'Erro PyODBC ao buscar utilizador: {e}', exc_info=True)
            return None
        except Exception as e:
            st.error(f'Erro inesperado (PyODBC) ao buscar utilizador: {e}')
            logger.error(f'Erro inesperado PyODBC ao buscar utilizador: {e}', exc_info=True)
            return None

    @staticmethod
    def get_user_by_id(schema: str, user_id: int) -> Optional[User]:  # noqa: PLR0911
        """fetch user by id"""

        if not db:
            st.error('Gerenciador do banco não disponível.')
            return None

        logger.info(f'Buscar utilizador {user_id} por ID')

        select_columns = ['ROWID', 'NOMUSR_0', 'USR_0', 'LOGIN_0', 'ZPWDHASH_0', 'ADDEML_0']
        columns = ', '.join([f'"{col}"' for col in select_columns])
        base_query = f'SELECT {columns} FROM "{schema}"."AUTILIS"'

        conditions = ['ENAFLG_0 = 2', 'ROWID = ?']
        params_list = [user_id]

        query = f'{base_query} WHERE {" AND ".join(conditions)};'
        params = tuple(params_list)

        try:
            with db.get_db() as conn:
                cursor = conn.cursor()
                logger.info(f'Executing query: {query} with params: {params}')
                cursor.execute(query, params)

                result = cursor.fetchone()
                if result is None:
                    logger.warning(f'No user found for ID: {user_id}')
                    return None

                user_data_dict = Generics.result_to_dict(cursor, result)
                if not user_data_dict:  # Verificação de segurança
                    logger.error('Generics.return_to_dict retornou None para uma linha não nula.')
                    return None

                try:
                    user_model = User(**user_data_dict)
                    logger.info(f'Utilizador encontrado e validado: {user_model.username} (ROWID: {user_model.id})')
                    return user_model
                except ValidationError as ve:
                    logger.error(f'Erro de validação Pydantic para dados do utilizador: {ve}', exc_info=True)
                    st.error(f'Os dados do utilizador recuperados são inválidos: {ve}')
                    return None
        except pyodbc.Error as e:
            st.error(f'Erro de banco de dados (PyODBC) ao buscar utilizador: {e}')
            logger.error(f'Erro PyODBC ao buscar utilizador: {e}', exc_info=True)
            return None
        except Exception as e:
            st.error(f'Erro inesperado (PyODBC) ao buscar utilizador: {e}')
            logger.error(f'Erro inesperado PyODBC ao buscar utilizador: {e}', exc_info=True)
            return None
