"""Utilitários genéricos para DataFrames pandas."""

from typing import Any, NamedTuple

import pandas as pd


class ComparisonTableData(NamedTuple):
    """Estrutura de dados para tabelas comparativas entre dois anos."""

    comparison_rows: list[Any]
    total_prev: pd.Series
    total_curr: pd.Series
    avg_prev: pd.Series
    avg_curr: pd.Series
    var_total_sales_copies: object
    var_total_sales_perc: object
    var_avg_sales_copies: object
    var_avg_sales_perc: object
    previous_year: int
    current_year: int


def format_value(val: Any) -> Any:
    """Formata um valor para apresentação (NaN -> `''`, float -> int, str -> strip)."""
    if pd.isna(val):
        return ''
    if isinstance(val, float):
        return int(val)
    if isinstance(val, str):
        return val.strip()
    return val


def equalize_rows(df1: pd.DataFrame, df2: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Iguala o número de linhas de dois DataFrames, preenchendo com `NaN`.

    Args:
        df1: Primeiro DataFrame.
        df2: Segundo DataFrame.

    Returns:
        Os dois DataFrames com o mesmo número de linhas e índice `0..n-1`.
    """
    max_length = max(len(df1), len(df2))
    full_index = pd.RangeIndex(start=0, stop=max_length, step=1)
    return (
        df1.reset_index(drop=True).reindex(full_index),
        df2.reset_index(drop=True).reindex(full_index),
    )
