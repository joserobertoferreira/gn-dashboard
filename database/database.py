import logging
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import MetaData, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from config.settings import DATABASE, DEBUG
from utils.generics import Generics

# Configurar logging
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database session manager."""

    def __init__(self, url: str, echo: bool = False):
        """Initialize the database session manager."""
        self.engine = create_engine(url, echo=echo)
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
        )
        self.metadata: MetaData = MetaData()

    # close connection
    def close(self):
        """Dispose of the engine connections."""
        if self.engine:
            self.engine.dispose()
            logger.info('Database engine disposed.')

    @contextmanager
    def get_db(self) -> Generator[Session, None, None]:
        """Provides a database session within a context."""
        if not self.SessionLocal:
            logger.error('SessionLocal is not initialized.')
            raise RuntimeError('Erro ao conectar ao banco de dados. Verifique os logs.')

        db_session: Optional[Session] = None
        try:
            db_session = self.SessionLocal()
            logger.debug(f'Sessão de banco de dados {id(db_session)} criada e sendo fornecida.')
            yield db_session
        except Exception as e:  # Captura exceções dentro do bloco 'with' que usa esta sessão
            logger.error(f'Exceção dentro do contexto da sessão de banco de dados {id(db_session)}: {e}', exc_info=True)
            raise
        finally:
            if db_session:
                logger.debug(f'Fechando sessão de banco de dados {id(db_session)}.')
                db_session.close()

    def commit_rollback(self, session: Session):  # noqa: PLR6301
        """Commits the session or rolls back in case of an error."""
        try:
            session.commit()
            logger.debug('Session committed successfully.')
        except Exception as e:
            session.rollback()
            logger.error(f'Session rollback due to error: {e}', exc_info=True)
            raise


# Initialize the database session manager
db = None

DB_CONNECTION_STRING = Generics().build_connection_string(config=DATABASE)

if DB_CONNECTION_STRING:
    try:
        # Passe echo=True para ver as queries SQL geradas, False para produção
        db = DatabaseManager(url=DB_CONNECTION_STRING, echo=DEBUG)  # type: ignore
        logger.info('DatabaseSessionManager initialized successfully.')
    except ValueError as ve:  # Erro específico da nossa validação de URL
        logger.error(f'Configuration Error: {ve}')
    except SQLAlchemyError as sa_err:  # Erros da criação do engine
        logger.error(f'SQLAlchemy Engine Creation Error: {sa_err}', exc_info=True)
    except Exception as e:  # Outros erros inesperados
        logger.error(f'Unexpected error initializing DatabaseSessionManager: {e}', exc_info=True)
