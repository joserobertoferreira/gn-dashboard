"""Configuração de tabelas (`st.dataframe`) usadas nos relatórios."""

from typing import Any

import streamlit as st


def config_columns_to_annual_revenue() -> dict[str, Any]:
    """Configuração das colunas da tabela de receita anual.

    Returns:
        Dicionário para o parâmetro `column_config` de `st.dataframe`.
    """
    return {
        'Customer': st.column_config.TextColumn(label='Cliente', width='small'),
        'Name': st.column_config.TextColumn(label='Nome', width='medium'),
        'Amount_invoice': st.column_config.NumberColumn(label='Faturas', width='small', format='%.2f'),
        'Amount_credit': st.column_config.NumberColumn(label='Notas de crédito', width='small', format='%.2f'),
        'Balance': st.column_config.NumberColumn(label='Saldo', width='small', format='%.2f'),
    }


def adjust_table_height(length: int, min_height: int = 200, max_height: int = 633, row_height: int = 30) -> int:
    """Calcula a altura da tabela em função do número de linhas.

    Args:
        length: Número de linhas.
        min_height: Altura mínima em píxeis.
        max_height: Altura máxima em píxeis.
        row_height: Altura de cada linha em píxeis.

    Returns:
        Altura ajustada em píxeis, entre `min_height` e `max_height`.
    """
    return min(max(min_height, length * row_height), max_height)
