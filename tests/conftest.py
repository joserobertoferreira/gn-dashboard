"""Fixtures partilhadas pelos testes."""

import pytest

from gn_dashboard.database.query_builder import QueryBuilder


class _FakeDatabaseManager:
    """Substituto do DatabaseManager: os testes não precisam de base de dados."""


@pytest.fixture
def query_builder() -> QueryBuilder:
    return QueryBuilder(db_manager=_FakeDatabaseManager())  # type: ignore[arg-type]
