"""Configuração do logging da aplicação (consola + ficheiros de info e erro)."""

import logging
import logging.config

from .settings import (
    LOG_CONSOLE_LEVEL,
    LOG_DIR,
    LOG_ERROR_FILE_ENABLED,
    LOG_ERROR_FILE_LEVEL,
    LOG_ERROR_FILENAME,
    LOG_INFO_FILE_ENABLED,
    LOG_INFO_FILE_LEVEL,
    LOG_INFO_FILENAME,
    LOG_ROOT_LEVEL,
)

_configured = False


def setup_logging(force: bool = False) -> None:
    """Configura o logging uma única vez por processo.

    O Streamlit volta a executar o script principal em cada interação; sem esta
    proteção os handlers de ficheiro seriam recriados a cada rerun.

    Args:
        force: Reconfigura mesmo que o logging já tenha sido configurado.
    """
    global _configured  # noqa: PLW0603
    if _configured and not force:
        return

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    handlers_config: dict[str, dict] = {
        'console': {
            'level': LOG_CONSOLE_LEVEL.upper(),
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        }
    }

    if LOG_INFO_FILE_ENABLED and LOG_INFO_FILENAME:
        handlers_config['info_file'] = {
            'level': LOG_INFO_FILE_LEVEL.upper(),
            'class': 'logging.FileHandler',
            'filename': str(LOG_DIR / LOG_INFO_FILENAME),
            'mode': 'a',
            'encoding': 'utf-8',
            'formatter': 'standard',
        }

    if LOG_ERROR_FILE_ENABLED and LOG_ERROR_FILENAME:
        handlers_config['error_file'] = {
            'level': LOG_ERROR_FILE_LEVEL.upper(),
            'class': 'logging.FileHandler',
            'filename': str(LOG_DIR / LOG_ERROR_FILENAME),
            'mode': 'a',
            'encoding': 'utf-8',
            'formatter': 'detailed',
        }

    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {'format': '%(asctime)s - %(levelname)s - %(name)s - %(message)s'},
            'detailed': {
                'format': (
                    '%(asctime)s - %(levelname)s - %(name)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s'
                )
            },
        },
        'handlers': handlers_config,
        'root': {'level': LOG_ROOT_LEVEL.upper(), 'handlers': list(handlers_config)},
    })

    _configured = True
    logging.getLogger(__name__).info(
        'Logging configurado. Root level: %s. Handlers: %s', LOG_ROOT_LEVEL, ', '.join(handlers_config)
    )
