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

    def _build_sql_params_for_where(  # noqa: PLR0912, PLR6301
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

            sanitized_column_for_param = ''.join(filter(str.isalnum, column.replace('.', '_')))
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
            elif operator == 'BETWEEN':
                if not isinstance(value, (list, tuple)) or len(value) != Chapter1.YES:
                    raise ValueError(
                        f'Value for BETWEEN operator on column {column} must be a list or tuple of two items.'
                    )

                start_param_name = f'{param_name}_start'
                end_param_name = f'{param_name}_end'
                sql_params[start_param_name] = Conversions.convert_value(value[0])
                sql_params[end_param_name] = Conversions.convert_value(value[1])

                where_parts.append(f'{column} {operator} :{start_param_name} AND :{end_param_name}')
            elif operator in {'IS NULL', 'IS NOT NULL'}:
                where_parts.append(f'{column} {operator}')
            else:
                where_parts.append(f'{column} {operator} :{param_name}')
                sql_params[param_name] = Conversions.convert_value(value)

        return ' AND '.join(where_parts), sql_params

    def execute_query(self, **kwargs) -> dict[str, Any]:  # noqa: PLR0912, PLR0914, PLR0915
        """
        Executa uma consulta SELECT pura.

        kwargs:
            table (str): Nome da tabela principal.
            table_alias (str, optional): Alias para a tabela principal.
            columns (List[Union[str, Dict[str, str]]], optional): Lista de colunas/expressões a selecionar.
                - str: "NomeTabelaOuAlias.NomeColuna"
                - Dict: {"column": "NomeTabelaOuAlias.NomeColuna", "alias": "nome_resultado"}
                - Dict: {"expression": "COUNT(*)", "alias": "total"}
                Default '*'.
            joins (List[Dict[str, str]], optional): Cláusulas JOIN.
                Ex: [
                    {
                        "type": "INNER",
                        "table": "OtherTable",
                        "alias": "ot",
                        "on": "MainTableAlias.fk_col = ot.pk_col"
                    }
                ]
            where_clauses (Dict[str, Tuple[str, Any]], optional): Condições para o WHERE.
                Ex: {"MainTableAlias.id": ("=", 1), "ot.status": ("IN", ["A", "B"])}
            options (Dict[str, str], optional): Cláusulas adicionais como GROUP BY, ORDER BY.
                Ex: {"group_by": "MainTableAlias.category", "order_by": "ot.name DESC"}
            limit (int, optional): Número máximo de registros (TOP para SQL Server, LIMIT para outros).
                                   (A lógica de dialeto para TOP/LIMIT não está totalmente implementada aqui)
        """
        main_table: Optional[str] = kwargs.get('table')
        if not main_table:
            return {'status': 'error', 'message': 'Table name is required.', 'data': None}

        main_table_alias: Optional[str] = kwargs.get('table_alias')
        columns_list: Optional[list[Union[str, dict[str, str]]]] = kwargs.get('columns')
        joins: Optional[list[dict[str, str]]] = kwargs.get('joins')
        where_clauses_input: Optional[dict[str, Tuple[str, Any]]] = kwargs.get('where_clauses')
        options: Optional[dict[str, str]] = kwargs.get('options', {})
        limit: Optional[int] = kwargs.get('limit')

        select_parts = []

        if not columns_list:
            select_parts.append('*')
        else:
            for col in columns_list:
                if isinstance(col, str):
                    # Coluna simples, pode ser um alias ou nome completo
                    select_parts.append(col)
                elif isinstance(col, dict):
                    # Coluna com alias ou expressão
                    if 'column' in col:
                        select_parts.append(f'{col["column"]} AS {col["alias"]}')
                    elif 'expression' in col and 'alias' in col:
                        select_parts.append(f'{col["expression"]} AS {col["alias"]}')
                    elif 'column' in col and 'alias' in col:
                        select_parts.append(f'{col["column"]} AS {col["alias"]}')
                    else:
                        logger.warning(f'Item de coluna malformado ignorado: {col}')
                else:
                    logger.warning(f'Tipo de item de coluna inesperado ignorado: {col}')

        select_clause = ', '.join(select_parts) if select_parts else '*'

        # TOP clause for SQL Server (adapt if using a different dialect)
        top_clause = f'TOP {int(limit)}' if limit and limit > 0 else ''

        table = main_table_alias if main_table_alias else main_table

        from_clause = f'FROM {table}'

        if main_table_alias:
            from_clause += f' AS {main_table_alias}'

        join_parts = []
        if joins:
            for join in joins:
                join_type = join.get('type', 'INNER').upper()
                join_table = join.get('table')
                join_alias = join.get('alias')
                on_condition = join.get('on')

                if not join_table or not on_condition:
                    logger.warning(f'Item de JOIN malformado ignorado (falta tabela ou condição ON): {join}')
                    continue

                join_clause_part = f'{join_type} JOIN {join_table}'
                if join_alias:
                    join_clause_part += f' AS {join_alias}'

                join_clause_part += f' ON {on_condition}'
                join_parts.append(join_clause_part)

        if join_parts:
            from_clause += ' ' + ' '.join(join_parts)

        query_string = f'SELECT {top_clause} {select_clause} {from_clause}'

        final_sql_params: dict[str, Any] = {}

        if where_clauses_input:
            where_sql, where_params = self._build_sql_params_for_where(where_clauses_input)
            if where_sql:
                query_string += f' WHERE {where_sql}'
                final_sql_params.update(where_params)

        if options:
            if 'group_by' in options and options['group_by']:
                query_string += f' GROUP BY {options["group_by"]}'
            if 'order_by' in options and options['order_by']:
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

                return {
                    'status': 'success',
                    'message': 'Query executed successfully' if fetched_data else 'No results found',
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
