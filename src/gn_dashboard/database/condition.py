"""Representação de uma condição `WHERE` (operador + valor)."""

from typing import Any, Iterator


class Condition:
    """Condição de filtro usada pelo [`QueryBuilder`][gn_dashboard.database.query_builder.QueryBuilder].

    Comporta-se como um tuplo `(operator, value)`.

    Args:
        operator: Operador SQL (`=`, `<>`, `IN`, `BETWEEN`, `IS NULL`, ...).
        value: Valor a comparar.
    """

    def __init__(self, operator: str, value: Any):
        self.operator = operator
        self.value = value

    def __repr__(self) -> str:
        return f'Condition(operator={self.operator}, value={self.value})'

    def __iter__(self) -> Iterator[Any]:
        yield self.operator
        yield self.value

    def __getitem__(self, index: int) -> Any:
        return (self.operator, self.value)[index]

    def __len__(self) -> int:
        return 2

    def as_tuple(self) -> tuple[str, Any]:
        """Devolve a condição como tuplo `(operator, value)`."""
        return self.operator, self.value
