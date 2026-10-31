"""Construção e execução de SQL "cru" (SELECT/INSERT/UPDATE/DELETE) com parâmetros nomeados.

Os nomes de tabelas e colunas são interpolados diretamente no SQL: **nunca** devem vir
de input do utilizador. Os valores são sempre passados como parâmetros.
"""

import logging
from typing import Any, Mapping, Optional, Union

from sqlalchemy import text
from sqlalchemy.engine import Result
from sqlalchemy.exc import SQLAlchemyError

from gn_dashboard.core.settings import DATABASE
from gn_dashboard.utils.conversions import Conversions

from .condition import Condition
from .session import DatabaseManager

logger = logging.getLogger(__name__)

#: Uma condição WHERE: objeto `Condition` ou tuplo `(operator, value)`.
WhereCondition = Union[tuple[str, Any], Condition]
#: Uma coluna do SELECT: string ou dicionário com `column`/`expression` e `alias`.
ColumnSpec = Union[str, dict[str, str]]

_PAIR_LENGTH = 2


class QueryBuilder:
    """Constrói e executa queries SQL sobre um [`DatabaseManager`][gn_dashboard.database.session.DatabaseManager].

    Args:
        db_manager: Gestor da base de dados.

    Raises:
        ValueError: Se `db_manager` for `None`.
    """

    def __init__(self, db_manager: Optional[DatabaseManager]):
        if not db_manager:
            raise ValueError('DatabaseManager instance is required.')
        self.db_manager = db_manager
        self.schema = str(DATABASE.get('SCHEMA') or '')

    # ------------------------------------------------------------------ #
    # Construção de SQL (sem acesso à base de dados)
    # ------------------------------------------------------------------ #
    @staticmethod
    def build_where(  # noqa: PLR0912
        where_clauses: Optional[Mapping[str, WhereCondition]],
        param_prefix: str = 'where',
    ) -> tuple[str, dict[str, Any]]:
        """Constrói a cláusula WHERE e o dicionário de parâmetros.

        Args:
            where_clauses: Mapeamento `coluna -> condição`. Ex.:
                `{'t.id': ('=', 1), 't.status': ('IN', ['A', 'B'])}`.
            param_prefix: Prefixo dos nomes dos parâmetros gerados.

        Returns:
            Tuplo `(sql_sem_WHERE, parametros)`; `('', {})` se não houver condições.

        Raises:
            ValueError: Se uma condição for inválida.
        """
        if not where_clauses:
            return '', {}

        where_parts: list[str] = []
        sql_params: dict[str, Any] = {}

        for param_idx, (column, condition_obj) in enumerate(where_clauses.items()):
            if isinstance(condition_obj, Condition):
                operator, value = condition_obj.operator.upper(), condition_obj.value
            elif isinstance(condition_obj, tuple) and len(condition_obj) == _PAIR_LENGTH:
                operator, value = str(condition_obj[0]).upper(), condition_obj[1]
            else:
                raise ValueError(
                    f'Invalid condition for column {column}. Expected Condition object or (operator, value) tuple.'
                )

            sanitized = ''.join(filter(str.isalnum, column.replace('.', '_')))
            param_name = f'{param_prefix}_{sanitized}_{param_idx}'

            if operator in {'IN', 'NOT IN'}:
                if not isinstance(value, (list, tuple)):
                    raise ValueError(f'Value for {operator} operator on column {column} must be a list or tuple.')
                if not value:
                    # IN () vazio nunca é verdadeiro; NOT IN () vazio é sempre verdadeiro
                    where_parts.append('1 = 0' if operator == 'IN' else '1 = 1')
                    continue
                placeholders = []
                for i, item_val in enumerate(value):
                    item_param = f'{param_name}_in_{i}'
                    placeholders.append(f':{item_param}')
                    sql_params[item_param] = Conversions.convert_value(item_val)
                where_parts.append(f'{column} {operator} ({", ".join(placeholders)})')
            elif operator == 'BETWEEN':
                if not isinstance(value, (list, tuple)) or len(value) != _PAIR_LENGTH:
                    raise ValueError(
                        f'Value for BETWEEN operator on column {column} must be a list or tuple of two items.'
                    )
                sql_params[f'{param_name}_start'] = Conversions.convert_value(value[0])
                sql_params[f'{param_name}_end'] = Conversions.convert_value(value[1])
                where_parts.append(f'{column} BETWEEN :{param_name}_start AND :{param_name}_end')
            elif operator in {'IS NULL', 'IS NOT NULL'}:
                where_parts.append(f'{column} {operator}')
            else:
                where_parts.append(f'{column} {operator} :{param_name}')
                sql_params[param_name] = Conversions.convert_value(value)

        return ' AND '.join(where_parts), sql_params

    @staticmethod
    def _build_select_list(columns: Optional[list[ColumnSpec]]) -> str:
        select_parts: list[str] = []
        for col in columns or []:
            if isinstance(col, str):
                select_parts.append(col)
            elif isinstance(col, dict):
                source = col.get('column') or col.get('expression')
                if not source:
                    logger.warning('Item de coluna malformado ignorado: %s', col)
                    continue
                alias = col.get('alias')
                select_parts.append(f'{source} AS {alias}' if alias else source)
            else:
                logger.warning('Tipo de item de coluna inesperado ignorado: %s', col)
        return ', '.join(select_parts) if select_parts else '*'

    @staticmethod
    def _build_joins(joins: Optional[list[dict[str, str]]]) -> str:
        join_parts: list[str] = []
        for join in joins or []:
            join_table = join.get('table')
            on_condition = join.get('on')
            if not join_table or not on_condition:
                logger.warning('Item de JOIN malformado ignorado (falta tabela ou condição ON): %s', join)
                continue
            part = f'{join.get("type", "INNER").upper()} JOIN {join_table}'
            if join.get('alias'):
                part += f' AS {join["alias"]}'
            join_parts.append(f'{part} ON {on_condition}')
        return ' '.join(join_parts)

    def build_select(self, **kwargs: Any) -> tuple[str, dict[str, Any]]:
        """Constrói uma query SELECT.

        Aceita os mesmos argumentos que
        [`execute_query`][gn_dashboard.database.query_builder.QueryBuilder.execute_query].

        Returns:
            Tuplo `(sql, parametros)`.

        Raises:
            ValueError: Se `table` não for indicada.
        """
        main_table: Optional[str] = kwargs.get('table')
        if not main_table:
            raise ValueError('Table name is required.')

        alias: Optional[str] = kwargs.get('table_alias')
        options: dict[str, Any] = kwargs.get('options') or {}
        limit: Optional[int] = kwargs.get('limit')

        top_clause = f'TOP {int(limit)} ' if limit and limit > 0 else ''
        select_clause = self._build_select_list(kwargs.get('columns'))

        from_clause = f'FROM {main_table}'
        if alias:
            from_clause += f' AS {alias}'
        joins_sql = self._build_joins(kwargs.get('joins'))
        if joins_sql:
            from_clause += f' {joins_sql}'

        sql = f'SELECT {top_clause}{select_clause} {from_clause}'
        params: dict[str, Any] = {}

        where_sql, where_params = self.build_where(kwargs.get('where_clauses'))
        if where_sql:
            sql += f' WHERE {where_sql}'
            params.update(where_params)

        for key, keyword in (('group_by', 'GROUP BY'), ('order_by', 'ORDER BY')):
            value = options.get(key)
            if value:
                if isinstance(value, (list, tuple)):
                    value = ', '.join(value)
                sql += f' {keyword} {value}'

        return sql, params

    # ------------------------------------------------------------------ #
    # Execução
    # ------------------------------------------------------------------ #
    def execute_query(self, **kwargs: Any) -> dict[str, Any]:
        """Executa uma consulta SELECT.

        Keyword Args:
            table (str): Nome da tabela principal (obrigatório).
            table_alias (str): Alias da tabela principal.
            columns (list): Colunas a selecionar. Cada item pode ser uma string
                (`'t.COL AS nome'`) ou um dicionário `{'column'|'expression': ..., 'alias': ...}`.
                Por omissão `*`.
            joins (list[dict]): JOINs, ex.: `[{'type': 'LEFT', 'table': 'X', 'alias': 'x', 'on': 't.a = x.a'}]`.
            where_clauses (dict): Condições WHERE
                (ver [`build_where`][gn_dashboard.database.query_builder.QueryBuilder.build_where]).
            options (dict): `group_by` e/ou `order_by` (string ou lista).
            limit (int): Número máximo de registos (`TOP n`, SQL Server).

        Returns:
            Dicionário com `status` (`'success'`/`'error'`), `message`, `columns`, `records` e `data`.
        """
        try:
            query_string, params = self.build_select(**kwargs)
        except ValueError as e:
            return {'status': 'error', 'message': str(e), 'records': 0, 'data': None}

        logger.debug('Executing query: %s with params: %s', query_string, params)

        try:
            with self.db_manager.get_db() as session:
                result: Result = session.connection().execute(text(query_string), params)
                column_names = list(result.keys())
                fetched_data = [dict(row) for row in result.mappings().all()]
                return {
                    'status': 'success',
                    'message': 'Query executed successfully' if fetched_data else 'No results found',
                    'columns': column_names,
                    'records': len(fetched_data),
                    'data': fetched_data,
                }
        except SQLAlchemyError as e:
            logger.error('SQLAlchemyError executing query: %s', e, exc_info=True)
            return {'status': 'error', 'message': f'Error executing query: {e}', 'records': 0, 'data': None}
        except Exception as e:  # noqa: BLE001
            logger.error('Unexpected error executing query: %s', e, exc_info=True)
            return {'status': 'error', 'message': f'Unexpected error: {e}', 'records': 0, 'data': None}

    def execute_dml(self, sql_query: str, params: dict[str, Any]) -> dict[str, Any]:
        """Executa INSERT/UPDATE/DELETE numa transação.

        Args:
            sql_query: SQL com parâmetros nomeados (`:nome`).
            params: Valores dos parâmetros.

        Returns:
            Dicionário com `status`, `message` e, em caso de sucesso, `affected_rows`.
        """
        logger.debug('Executing DML: %s with params: %s', sql_query, params)
        try:
            with self.db_manager.get_db() as session:
                result: Result = session.connection().execute(text(sql_query), params)
                affected_rows = result.rowcount
                self.db_manager.commit_rollback(session)
                return {'status': 'success', 'message': 'DML executed successfully.', 'affected_rows': affected_rows}
        except SQLAlchemyError as e:
            logger.error('SQLAlchemyError during DML execution: %s', e, exc_info=True)
            return {'status': 'error', 'message': f'Error executing DML: {e}'}
        except Exception as e:  # noqa: BLE001
            logger.error('Unexpected error during DML execution: %s', e, exc_info=True)
            return {'status': 'error', 'message': f'Unexpected error during DML: {e}'}

    def execute_insert(self, table_name: str, values_columns: dict[str, Any]) -> dict[str, Any]:
        """Insere um registo.

        Args:
            table_name: Tabela de destino.
            values_columns: Mapeamento `coluna -> valor`.
        """
        if not table_name or not isinstance(values_columns, dict) or not values_columns:
            return {'status': 'error', 'message': 'Table name and values_columns (non-empty dict) are required.'}

        params = {f'ins_{i}': Conversions.convert_value(v) for i, v in enumerate(values_columns.values())}
        columns_str = ', '.join(values_columns.keys())
        placeholders_str = ', '.join(f':{p}' for p in params)
        return self.execute_dml(f'INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders_str})', params)

    def execute_update(
        self, table_name: str, set_columns: dict[str, Any], where_clauses: Mapping[str, WhereCondition]
    ) -> dict[str, Any]:
        """Atualiza registos. A cláusula WHERE é obrigatória.

        Args:
            table_name: Tabela de destino.
            set_columns: Mapeamento `coluna -> novo valor`.
            where_clauses: Condições WHERE.
        """
        if not table_name or not set_columns or not where_clauses:
            return {
                'status': 'error',
                'message': 'Table name, set_columns (non-empty dict), and where_clauses (non-empty dict) are required.',
            }

        sql_params: dict[str, Any] = {}
        set_parts = []
        for idx, (col, val) in enumerate(set_columns.items()):
            set_parts.append(f'{col} = :set_param_{idx}')
            sql_params[f'set_param_{idx}'] = Conversions.convert_value(val)

        where_sql, where_params = self.build_where(where_clauses, param_prefix='update_where')
        if not where_sql:
            return {'status': 'error', 'message': 'WHERE clause is mandatory for UPDATE operations.'}

        sql_params.update(where_params)
        return self.execute_dml(f'UPDATE {table_name} SET {", ".join(set_parts)} WHERE {where_sql}', sql_params)

    def execute_delete(self, table_name: str, where_clauses: Mapping[str, WhereCondition]) -> dict[str, Any]:
        """Apaga registos. A cláusula WHERE é obrigatória.

        Args:
            table_name: Tabela de destino.
            where_clauses: Condições WHERE.
        """
        if not table_name or not where_clauses:
            return {
                'status': 'error',
                'message': 'Table name and where_clauses (non-empty dict) are required for DELETE.',
            }

        where_sql, sql_params = self.build_where(where_clauses, param_prefix='delete_where')
        if not where_sql:
            return {'status': 'error', 'message': 'WHERE clause is mandatory for DELETE operations.'}

        return self.execute_dml(f'DELETE FROM {table_name} WHERE {where_sql}', sql_params)


#: Nome antigo, mantido por compatibilidade.
DatabaseCoreManager = QueryBuilder
