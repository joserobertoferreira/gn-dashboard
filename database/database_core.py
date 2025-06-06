import logging
from typing import Any, Mapping, Optional, Tuple, Union

from sqlalchemy import text
from sqlalchemy.engine import Result
from sqlalchemy.exc import SQLAlchemyError

from config.settings import DATABASE
from utils.conversions import Conversions
from utils.local_menus import Chapter1

from .condition import Condition
from .database import DatabaseManager

logger = logging.getLogger(__name__)


class DatabaseCoreManager:
    def __init__(self, db_manager: 'DatabaseManager'):
        if not db_manager:
            raise ValueError('DatabaseManager instance is required.')
        self.db_manager = db_manager
        self.schema = str(DATABASE.get('SCHEMA', ''))

    def _build_sql_params_for_where(  # noqa: PLR6301
        self,
        where_clauses: Optional[Mapping[str, Union[Tuple[str, Any], Condition]]],
        param_prefix: str = 'where',
    ) -> Tuple[str, dict[str, Any]]:
        """
        Constrói a cláusula WHERE e o dicionário de parâmetros para SQLAlchemy.
        """
        if not where_clauses:
            return '', {}

        where_parts = []
        sql_params: dict[str, Any] = {}
        param_idx = 0

        for column, condition_obj in where_clauses.items():
            operator: str
            value: Any

            if isinstance(condition_obj, Condition):
                operator = condition_obj.operator
                value = condition_obj.value
            elif isinstance(condition_obj, tuple) and len(condition_obj) == Chapter1.YES:
                # Esta parte do Union é usada por execute_query
                operator = condition_obj[0].upper()
                value = condition_obj[1]
            else:
                # Se chegar aqui com algo que não é Condition nem tupla (operator, value)
                # vindo de execute_query, é um erro de lógica interna ou tipo inesperado.
                # No contexto de execute_delete, condition_obj sempre será Condition.
                raise ValueError(
                    f'Invalid condition for column {column}. Expected Condition object or (operator, value) tuple.'
                )

            sanitized_column_for_param = ''.join(filter(str.isalnum, column))
            param_name = f'{param_prefix}_{sanitized_column_for_param}_{param_idx}'
            param_idx += 1

            if operator == 'IN':
                if not isinstance(value, (list, tuple)):
                    raise ValueError(f'Value for IN operator on column {column} must be a list or tuple.')

                if not value:
                    where_parts.append('1 = 0')
                    continue

                in_param_base_name = f'{param_prefix}_{sanitized_column_for_param}_{param_idx}_in'

                individual_placeholders = []
                for i, item_val in enumerate(value):
                    # Criar um nome de parâmetro único para cada item na lista IN
                    individual_param_name = f'{in_param_base_name}_{i}'
                    individual_placeholders.append(f':{individual_param_name}')
                    sql_params[individual_param_name] = Conversions.convert_value(item_val)

                where_parts.append(f'{column} {operator} ({", ".join(individual_placeholders)})')
            elif operator in {'IS NULL', 'IS NOT NULL'}:
                where_parts.append(f'{column} {operator}')
            else:
                where_parts.append(f'{column} {operator} :{param_name}')
                sql_params[param_name] = Conversions.convert_value(value)

        return ' AND '.join(where_parts), sql_params

    def execute_query(self, **kwargs) -> dict[str, Any]:  # noqa: PLR0914
        """
        Executa uma consulta SELECT pura.

        kwargs:
            table (str): Nome da tabela principal.
            columns (List[str], optional): Lista de colunas a selecionar. Default '*'.
            where_clauses (dict[str, Tuple[str, Any]], optional): Condições para o WHERE.
                Ex: {"id": ("=", 1), "status": ("IN", ["A", "B"])}
            options (dict[str, str], optional): Cláusulas adicionais como GROUP BY, ORDER BY.
                Ex: {"group_by": "category", "order_by": "name DESC"}
            limit (int, optional): Número máximo de registros (TOP para SQL Server).
            joins (List[Tuple[str, str, str, str]], optional): Cláusulas JOIN.
                Ex: [("INNER", "OtherTable", "main_table_fk_col", "other_table_pk_col")]
                  (join_type, join_table, left_on_column_from_main_table, right_on_column_from_join_table)
        """
        table: Optional[str] = kwargs.get('table')
        if not table:
            return {'status': 'error', 'message': 'Table name is required.', 'data': None}

        columns_list: Optional[list[str]] = kwargs.get('columns')
        where_clauses_input: Optional[dict[str, Tuple[str, Any]]] = kwargs.get('where_clauses')
        options: Optional[dict[str, str]] = kwargs.get('options')
        limit: Optional[int] = kwargs.get('limit')
        joins: Optional[list[Tuple[str, str, str, str]]] = kwargs.get('joins')

        select_clause = ', '.join(columns_list) if columns_list else '*'

        # TOP clause for SQL Server (adapt if using a different dialect)
        top_clause = f'TOP {int(limit)}' if limit and limit > 0 else ''

        from_clause = f'FROM {table}'
        if joins:
            join_parts = []
            for join_type, join_table, left_col, right_col in joins:
                # Assuming left_col is from the primary 'table' or a previously joined table.
                # For simplicity here, assuming left_col is from the primary 'table'.
                # More complex scenarios might require alias.
                join_parts.append(
                    f'{join_type.upper()} JOIN {join_table} ON {table}.{left_col} = {join_table}.{right_col}'
                )
            from_clause += ' ' + ' '.join(join_parts)

        query_string = f'SELECT {top_clause} {select_clause} {from_clause}'

        final_sql_params: dict[str, Any] = {}

        if where_clauses_input:
            where_sql, where_params = self._build_sql_params_for_where(where_clauses_input)
            if where_sql:
                query_string += f' WHERE {where_sql}'
                final_sql_params.update(where_params)

        if options:
            if 'group_by' in options:
                query_string += f' GROUP BY {options["group_by"]}'
            if 'order_by' in options:
                query_string += f' ORDER BY {options["order_by"]}'

        logger.debug(f'Executing query: {query_string} with params: {final_sql_params}')

        try:
            with self.db_manager.get_db() as session:
                connection = session.connection()
                result: Result = connection.execute(text(query_string), final_sql_params)

                # For SELECT, it's good practice to not commit or rollback unless there's a specific reason.
                # SQLAlchemy sessions often don't require explicit commit for SELECTs on their own.
                # The context manager will close the session properly.

                column_names = list(result.keys())
                # `mappings().all()` returns a list of RowMapping objects (dict-like)
                fetched_data = [dict(row) for row in result.mappings().all()]

                if not fetched_data:
                    return {
                        'status': 'success',
                        'message': 'No results found',
                        'columns': column_names,
                        'records': 0,
                        'data': [],
                    }

                return {
                    'status': 'success',
                    'message': 'Query executed successfully',
                    'columns': column_names,
                    'records': len(fetched_data),
                    'data': fetched_data,
                }
        except SQLAlchemyError as e:
            logger.error(f'SQLAlchemyError executing query: {e}', exc_info=True)
            return {'status': 'error', 'message': f'Error executing query: {e}', 'data': None}
        except Exception as e:
            logger.error(f'Unexpected error executing query: {e}', exc_info=True)
            return {'status': 'error', 'message': f'Unexpected error: {e}', 'data': None}

    def execute_dml(self, sql_query: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Helper para executar INSERT, UPDATE, DELETE e lidar com transações.
        Retorna o número de linhas afetadas se aplicável e bem-sucedido.
        """
        logger.debug(f'Executing DML: {sql_query} with params: {params}')
        try:
            with self.db_manager.get_db() as session:
                connection = session.connection()
                result: Result = connection.execute(text(sql_query), params)
                # `rowcount` gives the number of rows affected by an UPDATE or DELETE.
                # For INSERT, it's often 1 per row (driver-dependent).
                # Not all drivers/DBs support rowcount reliably for all statements.
                affected_rows = result.rowcount

                # Commit a transação através do gerenciador de sessão do DatabaseManager
                self.db_manager.commit_rollback(session)  # Handles commit and rollback on error

                return {'status': 'success', 'message': 'DML executed successfully.', 'affected_rows': affected_rows}
        except SQLAlchemyError as e:
            # O commit_rollback no DatabaseManager já loga o erro se o commit falhar,
            # mas podemos logar o erro da execução aqui também.
            logger.error(f'SQLAlchemyError during DML execution: {e}', exc_info=True)
            # A exceção será propagada pelo commit_rollback se o rollback falhar,
            # ou se o erro ocorrer antes do commit_rollback ser chamado.
            return {'status': 'error', 'message': f'Error executing DML: {e}'}
        except Exception as e:
            logger.error(f'Unexpected error during DML execution: {e}', exc_info=True)
            return {'status': 'error', 'message': f'Unexpected error during DML: {e}'}

    def execute_insert(
        self,
        table_name: str,
        values_columns: dict[str, Any],
    ) -> dict[str, Any]:
        if not table_name or not isinstance(values_columns, dict) or not values_columns:
            return {'status': 'error', 'message': 'Table name and values_columns (non-empty dict) are required.'}

        columns_str = ', '.join(values_columns.keys())
        # Usar :key para os placeholders nomeados
        placeholders_str = ', '.join([f':{col}' for col in values_columns.keys()])

        sql_query = f'INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders_str})'

        # Os parâmetros já estão no formato {col_name: value}, que é o que text() espera.
        return self.execute_dml(sql_query, values_columns)

    def execute_update(
        self,
        table_name: str,
        set_columns: dict[str, Any],
        where_clauses: dict[str, Condition],
    ) -> dict[str, Any]:
        if (
            not table_name
            or not isinstance(set_columns, dict)
            or not set_columns
            or not isinstance(where_clauses, dict)
            or not where_clauses
        ):
            return {
                'status': 'error',
                'message': 'Table name, set_columns (non-empty dict), and where_clauses (non-empty dict) are required.',
            }

        set_parts = []
        sql_params: dict[str, Any] = {}
        param_idx = 0

        for col, val in set_columns.items():
            param_name = f'set_param_{param_idx}'
            set_parts.append(f'{col} = :{param_name}')
            sql_params[param_name] = Conversions.convert_value(val)
            param_idx += 1
        set_clause = ', '.join(set_parts)

        where_sql, where_params = self._build_sql_params_for_where(where_clauses, param_prefix='update_where')
        if not where_sql:  # Segurança: não permitir UPDATE sem WHERE por padrão
            return {'status': 'error', 'message': 'WHERE clause is mandatory for UPDATE operations.'}

        sql_params.update(where_params)
        sql_query = f'UPDATE {table_name} SET {set_clause} WHERE {where_sql}'

        return self.execute_dml(sql_query, sql_params)

    def execute_delete(
        self,
        table_name: str,
        where_clauses: dict[str, Condition],  # Mantendo a Condition
    ) -> dict[str, Any]:
        if not table_name or not isinstance(where_clauses, dict) or not where_clauses:
            return {
                'status': 'error',
                'message': 'Table name and where_clauses (non-empty dict) are required for DELETE.',
            }

        where_sql, sql_params = self._build_sql_params_for_where(where_clauses, param_prefix='delete_where')
        if not where_sql:  # Segurança: não permitir DELETE sem WHERE por padrão
            return {'status': 'error', 'message': 'WHERE clause is mandatory for DELETE operations.'}

        sql_query = f'DELETE FROM {table_name} WHERE {where_sql}'

        return self.execute_dml(sql_query, sql_params)
