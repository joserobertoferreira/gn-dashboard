"""Acesso a dados de clientes (tabela `BPCUSTOMER`)."""

import logging
from typing import Optional

from gn_dashboard.database.query_builder import QueryBuilder
from gn_dashboard.database.session import DatabaseManager, get_database_manager

logger = logging.getLogger(__name__)


class CustomerRepository:
    """Operações de base de dados relativas a clientes.

    Args:
        db: Gestor da base de dados; por omissão usa o partilhado pelo processo.
    """

    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db or get_database_manager()

    def fetch_raw_customers(self, filter: Optional[list[str]] = None) -> list[dict[str, str]]:  # noqa: A002
        """Devolve código e nome dos clientes.

        Args:
            filter: Lista de códigos de cliente; `None` para todos.

        Returns:
            Lista de dicionários `{'code': ..., 'name': ...}` ordenada por código.
        """
        if not self.db:
            logger.error('Base de dados não disponível.')
            return []

        query = QueryBuilder(db_manager=self.db)
        query_params: dict = {
            'table': f'{query.schema}.BPCUSTOMER',
            'columns': ['BPCNUM_0 AS code', 'BPCNAM_0 AS name'],
            'options': {'order_by': 'BPCNUM_0'},
        }

        if filter:
            codes = [c.upper() for c in filter if isinstance(c, str)]
            query_params['where_clauses'] = {'BPCNUM_0': ('IN', codes)}

        result = query.execute_query(**query_params)

        if result['status'] != 'success':
            logger.error('Erro ao consultar a base de dados: %s', result.get('message'))
            return []

        if result['records'] == 0:
            logger.warning('Nenhum cliente encontrado na base de dados.')
            return []

        return result['data']
