import logging
from typing import Optional

from database.database import db
from database.database_core import DatabaseCoreManager

logger = logging.getLogger(__name__)


class CustomerRepository:
    """
    Repository for customer-related database operations.
    """

    def __init__(self):
        self.db = db

    def fetch_raw_customers(self, filter: Optional[list[str]]) -> list[dict[str, str]]:
        db_core = DatabaseCoreManager(db_manager=self.db)

        query_params = {
            'table': f'{db_core.schema}.BPCUSTOMER',
            'columns': ['BPCNUM_0 AS code', 'BPCNAM_0 as name'],
            'order_by': ['BPCNUM_0'],
        }

        if isinstance(filter, list) and len(filter) > 0:
            filter = [c.upper() for c in filter if isinstance(c, str)]
            query_params['where_clauses'] = {'BPCNUM_0': ('IN', filter)}

        result = db_core.execute_query(**query_params)

        if result is None or result['status'] != 'success':
            logger.error('Erro ao consultar o banco de dados. Verifique os logs para mais detalhes.')
            return []

        if result['records'] == 0:
            logger.warning('Nenhum cliente encontrado no banco de dados.')
            return []

        return result['data']
