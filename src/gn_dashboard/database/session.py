"""Gestão do engine e das sessões SQLAlchemy."""

import logging
from contextlib import contextmanager
from functools import lru_cache
from typing import Generator, Optional, Union

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from gn_dashboard.core.settings import DATABASE, DEBUG
from gn_dashboard.database.connection import build_connection_string

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gestor do engine SQLAlchemy e das sessões.

    Args:
        url: URL de ligação à base de dados.
        echo: Se `True`, regista no log todas as queries SQL geradas.
    """

    def __init__(self, url: Union[str, URL], echo: bool = False):
        self.engine = create_engine(url, echo=echo, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)

    def close(self) -> None:
        """Liberta as ligações do engine."""
        if self.engine:
            self.engine.dispose()
            logger.info('Database engine disposed.')

    @contextmanager
    def get_db(self) -> Generator[Session, None, None]:
        """Fornece uma sessão de base de dados dentro de um bloco `with`.

        Yields:
            Uma sessão SQLAlchemy, fechada automaticamente no fim do bloco.
        """
        db_session: Optional[Session] = None
        try:
            db_session = self.SessionLocal()
            logger.debug('Sessão de base de dados %s criada.', id(db_session))
            yield db_session
        except Exception as e:
            logger.error('Exceção na sessão de base de dados %s: %s', id(db_session), e, exc_info=True)
            raise
        finally:
            if db_session:
                logger.debug('A fechar a sessão de base de dados %s.', id(db_session))
                db_session.close()

    @staticmethod
    def commit_rollback(session: Session) -> None:
        """Faz commit da sessão ou rollback em caso de erro (a exceção é propagada)."""
        try:
            session.commit()
            logger.debug('Session committed successfully.')
        except Exception as e:
            session.rollback()
            logger.error('Session rollback due to error: %s', e, exc_info=True)
            raise


@lru_cache(maxsize=1)
def get_database_manager() -> Optional[DatabaseManager]:
    """Devolve o `DatabaseManager` partilhado pelo processo (criado na primeira chamada).

    Returns:
        O gestor da base de dados, ou `None` se a configuração for inválida.
    """
    url = build_connection_string(DATABASE)
    if url is None:
        return None

    try:
        manager = DatabaseManager(url=url, echo=DEBUG)
        logger.info('DatabaseManager inicializado com sucesso.')
        return manager
    except SQLAlchemyError as sa_err:
        logger.error('Erro ao criar o engine SQLAlchemy: %s', sa_err, exc_info=True)
    except Exception as e:  # noqa: BLE001
        logger.error('Erro inesperado ao inicializar o DatabaseManager: %s', e, exc_info=True)
    return None
