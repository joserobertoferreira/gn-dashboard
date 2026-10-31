"""Configuração central da aplicação.

Os valores sensíveis são lidos de `.streamlit/secrets.toml` (via `st.secrets`).
Se o ficheiro não existir (por exemplo, em testes ou na geração da documentação),
são usados valores por omissão vazios, para que o módulo possa ser importado sem erro.
"""

from datetime import date, datetime
from pathlib import Path
from typing import Any

import streamlit as st

# Raiz do projeto: src/gn_dashboard/core/settings.py -> parents[3]
BASE_DIR = Path(__file__).resolve().parents[3]
PACKAGE_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = BASE_DIR / 'assets'
IMAGES_DIR = ASSETS_DIR / 'images'
VIEWS_DIR = PACKAGE_DIR / 'views'


def _secret_section(section: str) -> dict[str, Any]:
    """Devolve uma secção de `st.secrets` como dicionário, ou `{}` se não existir.

    Args:
        section: Nome da secção no ficheiro `secrets.toml`.

    Returns:
        Dicionário com os valores da secção.
    """
    try:
        return dict(st.secrets.get(section, {}))
    except Exception:  # noqa: BLE001 - secrets.toml inexistente ou inválido
        return {}


def _resolve_debug() -> bool:
    """Determina o modo debug.

    Ordem de prioridade:

    1. `[app] debug = true|false` (chave recomendada).
    2. `[debug] production = true|false` (chave antiga; debug é o inverso de production).
    3. `False`.
    """
    app_section = _secret_section('app')
    if 'debug' in app_section:
        return bool(app_section['debug'])

    legacy = _secret_section('debug')
    if 'production' in legacy:
        return not bool(legacy['production'])

    return False


_db = _secret_section('database')

#: Parâmetros de ligação à base de dados SQL Server.
DATABASE: dict[str, Any] = {
    'SERVER': _db.get('server'),
    'DATABASE': _db.get('database'),
    'SCHEMA': _db.get('schema'),
    'USERNAME': _db.get('username'),
    'PASSWORD': _db.get('password'),
    'DRIVER': _db.get('driver', 'ODBC Driver 17 for SQL Server'),
    'TRUSTED_CONNECTION': _db.get('trusted_connection', 'no'),
}

#: Modo debug (ativa, entre outros, o `echo` das queries SQL).
DEBUG: bool = _resolve_debug()

# Configuração de logging
LOG_DIR = BASE_DIR / 'logs'
LOG_ROOT_LEVEL = 'DEBUG'
LOG_CONSOLE_LEVEL = 'INFO'
LOG_INFO_FILE_ENABLED = True
LOG_INFO_FILENAME = 'app_info.log'
LOG_INFO_FILE_LEVEL = 'INFO'
LOG_ERROR_FILE_ENABLED = True
LOG_ERROR_FILENAME = 'app_error.log'
LOG_ERROR_FILE_LEVEL = 'ERROR'

# Valores por omissão das tabelas Sage X3 (data "vazia" em SQL Server)
DEFAULT_LEGACY_DATE = date(1753, 1, 1)
DEFAULT_LEGACY_DATETIME = datetime(1753, 1, 1)
