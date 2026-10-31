"""Classe base declarativa do SQLAlchemy, com o schema Sage X3 configurado."""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from gn_dashboard.core.settings import DATABASE

#: Metadata partilhada por todos os modelos; o schema vem de `[database] schema`.
metadata_obj = MetaData(schema=DATABASE.get('SCHEMA') or None)


class Base(DeclarativeBase):
    """Classe base de todos os modelos SQLAlchemy.

    Usa uma metadata própria para que todas as tabelas fiquem no schema configurado.
    """

    metadata = metadata_obj
