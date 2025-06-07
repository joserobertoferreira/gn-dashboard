import logging
from typing import Optional

from database.database import db
from database.database_core import DatabaseCoreManager

logger = logging.getLogger(__name__)


class CountryRepository:
    """
    Repository for country-related database operations.
    """

    def __init__(self):
        self.db = db

    def fetch_countries(self, country: Optional[list[str]]) -> list[str]:
        db_core = DatabaseCoreManager(db_manager=self.db)

        query_params = {
            'table': f'{db_core.schema}.ZTABCOUNTRY',
            'columns': ['CRY_0', 'CRYDES_0'],
            'order_by': ['CRY_0'],
        }

        if isinstance(country, list) and len(country) > 0:
            country = [c.upper() for c in country if isinstance(c, str)]
            query_params['where_clauses'] = {'CRY_0': ('IN', country)}

        result = db_core.execute_query(**query_params)

        countries = []

        if result is None or result['status'] != 'success':
            logger.error('Erro ao consultar o banco de dados. Verifique os logs para mais detalhes.')
            return countries

        if result['records'] == 0:
            logger.warning('Nenhum país encontrado no banco de dados.')
            return countries

        for data in result['data']:
            countries.append(data.get('CRYDES_0', ''))

        return countries
