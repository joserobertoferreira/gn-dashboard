"""Construção da URL de ligação SQLAlchemy para SQL Server (pyodbc)."""

import logging
import platform
from typing import Any, Optional

import sqlalchemy as sa

logger = logging.getLogger(__name__)

SUPPORTED_ODBC_DRIVERS = frozenset({'ODBC Driver 17 for SQL Server', 'ODBC Driver 18 for SQL Server'})


def check_odbc_driver(driver_name: str) -> Optional[str]:
    """Verifica se o driver ODBC é suportado no sistema operativo atual.

    Args:
        driver_name: Nome do driver ODBC.

    Returns:
        `None` se o driver for suportado, caso contrário uma mensagem de erro.
    """
    os_name = platform.system()
    if os_name not in {'Windows', 'Linux', 'Darwin'}:
        return f"Sistema operativo '{os_name}' não suportado."
    if driver_name not in SUPPORTED_ODBC_DRIVERS:
        return f"Driver '{driver_name}' não é suportado em {os_name}."
    return None


def _is_truthy(value: Any) -> bool:
    return str(value).strip().lower() in {'1', 'true', 'yes', 'sim', 'y'}


def build_connection_string(config: dict[str, Any]) -> Optional[sa.engine.URL]:
    """Constrói a URL de ligação à base de dados.

    Args:
        config: Dicionário com as chaves `SERVER`, `DATABASE`, `USERNAME`, `PASSWORD`,
            `DRIVER` e `TRUSTED_CONNECTION` (ver `gn_dashboard.core.settings.DATABASE`).

    Returns:
        A URL SQLAlchemy, ou `None` se faltar o servidor ou a base de dados.
    """
    if not config.get('SERVER') or not config.get('DATABASE'):
        logger.error('Configuração da base de dados incompleta (server/database em falta).')
        return None

    query: dict[str, str] = {'driver': str(config.get('DRIVER') or 'ODBC Driver 17 for SQL Server')}
    trusted = _is_truthy(config.get('TRUSTED_CONNECTION', 'no'))
    if trusted:
        query['Trusted_Connection'] = 'yes'

    url = sa.engine.URL.create(
        drivername='mssql+pyodbc',
        host=config['SERVER'],
        database=config['DATABASE'],
        username=None if trusted else config.get('USERNAME'),
        password=None if trusted else config.get('PASSWORD'),
        query=query,
    )

    # render_as_string oculta a password por omissão
    logger.info('String de ligação criada: %s', url.render_as_string(hide_password=True))
    return url
