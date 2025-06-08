from typing import Any, NamedTuple

import pandas as pd
import streamlit as st


class ComparisonTableData(NamedTuple):
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


def config_columns_to_annual_revenue() -> dict[str, Any]:
    """
    Configures the columns for the annual revenue table.
    Returns:
        dict[str, Any]: A dictionary containing the columns configuration.
    """

    columns_config = {
        'Customer': st.column_config.TextColumn(label='Cliente', width='small'),
        'Name': st.column_config.TextColumn(label='Nome', width='medium'),
        'Amount_invoice': st.column_config.NumberColumn(label='Total', width='small'),
        'Amount_credit': st.column_config.NumberColumn(label='Total', width='small'),
        'Balance': st.column_config.NumberColumn(label='Saldo', width='small'),
    }

    return columns_config


def format_value(val):
    if pd.isna(val):
        return ''
    elif isinstance(val, float):
        return int(val)
    elif isinstance(val, str):
        return val.strip()
    else:
        return val


def equalize_rows(df1: pd.DataFrame, df2: pd.DataFrame):
    df1 = df1.reset_index(drop=True)
    df2 = df2.reset_index(drop=True)

    max_length = max(len(df1), len(df2))
    full_index = pd.RangeIndex(start=0, stop=max_length, step=1)
    df1_equalized = df1.reindex(full_index).reset_index(drop=True)
    df2_equalized = df2.reindex(full_index).reset_index(drop=True)

    return df1_equalized, df2_equalized


def adjust_table_height(length: int, min_height: int = 200, max_height: int = 633, row_height: int = 30) -> int:
    """
    Adjusts the height of the table based on the number of rows.
    Args:
        table (pd.DataFrame): The DataFrame to adjust.
        min_height (int): The minimum height in pixels.
        max_height (int): The maximum height in pixels.
        row_height (int): The height of each row in pixels.
    Returns:
        int: The adjusted height in pixels.
    """
    adjusted_height = length * row_height
    return min(max(min_height, adjusted_height), max_height)
