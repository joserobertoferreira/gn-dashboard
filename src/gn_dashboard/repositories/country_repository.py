"""Acesso a dados de países (tabela `ZTABCOUNTRY`)."""

import logging
from typing import Optional

from gn_dashboard.database.query_builder import QueryBuilder
from gn_dashboard.database.session import DatabaseManager, get_database_manager

logger = logging.getLogger(__name__)


class CountryRepository:
    """Operações de base de dados relativas a países.

    Args:
        db: Gestor da base de dados; por omissão usa o partilhado pelo processo.
    """

    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db or get_database_manager()

    def fetch_countries(self, country: Optional[list[str]] = None) -> list[str]:
        """Devolve as descrições dos países, opcionalmente filtradas por código.

        Args:
            country: Lista de códigos de país (ex.: `['PT', 'ES']`); `None` para todos.

        Returns:
            Lista com as descrições dos países, ordenada por código.
        """
        if not self.db:
            logger.error('Base de dados não disponível.')
            return []

        query = QueryBuilder(db_manager=self.db)
        query_params: dict = {
            'table': f'{query.schema}.ZTABCOUNTRY',
            'columns': ['CRY_0', 'CRYDES_0'],
            'options': {'order_by': 'CRY_0'},
        }

        if country:
            codes = [c.upper() for c in country if isinstance(c, str)]
            query_params['where_clauses'] = {'CRY_0': ('IN', codes)}

        result = query.execute_query(**query_params)

        if result['status'] != 'success':
            logger.error('Erro ao consultar a base de dados: %s', result.get('message'))
            return []

        if result['records'] == 0:
            logger.warning('Nenhum país encontrado na base de dados.')
            return []

        return [row.get('CRYDES_0', '') for row in result['data']]
