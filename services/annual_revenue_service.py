import logging

import pandas as pd
import streamlit as st

from config.settings import DATABASE
from database.database import db
from database.database_core import DatabaseCoreManager
from utils.local_menus import Chapter645

# from utils.comparison_table_data import equalize_rows

logger = logging.getLogger(__name__)


class AnnualRevenueService:
    """
    Service class for handling annual revenue data.
    """

    def __init__(self):
        pass

    @staticmethod
    @st.cache_data(ttl=600)
    def fetch_revenue_data(start_year: int, end_year: int, invoice_type: int) -> pd.DataFrame:  # noqa: PLR6301
        """
        Fetches annual revenue data from the database for the years interval and countries.
        Args:
            start_year (int): Start year for the data.
            end_year (int): End year for the data.
            invoice_type (int): Type of invoice to filter the data.
        Returns:
            pd.DataFrame: DataFrame containing the annual revenue data.
        """

        if not db:  # Verifica se db e seu engine foram inicializados
            st.error('Gerenciador do banco não disponível.')
            logger.error('Gerenciador do banco não disponível.')
            return pd.DataFrame()

        schema = DATABASE.get('SCHEMA', None)
        if not schema:
            st.error('Esquema do banco de dados não definido.')
            logger.error('Esquema do banco de dados não definido.')
            return pd.DataFrame()

        if invoice_type not in Chapter645._value2member_map_:
            logger.error(f'Tipo de fatura inválido: {invoice_type}.')
            return pd.DataFrame()

        logger.info(f'Buscar dados de vendas entre {start_year} e {end_year}')

        db_core = DatabaseCoreManager(db_manager=db)

        result = db_core.execute_query(
            table=f'{schema}.SINVOICE',
            columns=[
                'YEAR(ACCDAT_0) AS Year',
                'BPR_0 AS Customer',
                'SUM(AMTATI_0) AS Amount',
            ],
            where_clauses={
                'INVTYP_0': ('=', invoice_type),
                'REVCANSTA_0': ('=', 0),
                'ORIMOD_0': ('=', 5),
                'YEAR(ACCDAT_0)': ('BETWEEN', (start_year, end_year)),
            },
            options={
                'group_by': 'YEAR(ACCDAT_0), BPR_0',
                'order_by': 'YEAR(ACCDAT_0), BPR_0',
            },
        )

        if result is None or result['records'] == 0:
            logger.warning(
                f'Nenhum dado encontrado para os parâmetros: '
                f'Início: {start_year}, Fim: {end_year}, Tipo de Fatura: {invoice_type}'
            )
            return pd.DataFrame()

        data = result['data']
        df = pd.DataFrame(data)

        if df.empty:
            logger.warning(
                f'Nenhum dado encontrado para os parâmetros: '
                f'Início: {start_year}, Fim: {end_year}, Tipo de Fatura: {invoice_type}'
            )
            return pd.DataFrame()

        logger.info(f'Dados brutos recebidos do banco ({len(df)} linhas). Colunas: {df.columns.tolist()}')

        return df

    @staticmethod
    def split_revenue_by_year(
        invoices: pd.DataFrame, credits: pd.DataFrame, start_year: int, end_year: int
    ) -> tuple[dict[int, pd.DataFrame], dict[int, pd.DataFrame]]:
        """
        Split the revenue data into separate DataFrames for each year.
        Args:
            invoices (pd.DataFrame): DataFrame containing invoice data.
            credits (pd.DataFrame): DataFrame containing credit data.
            start_year (int): Start year for the data.
            end_year (int): End year for the data.
        Returns:
            tuple: Two dictionaries with DataFrames for each year.
        """
        df_invoices = {}
        df_credits = {}

        for year in range(start_year, end_year + 1):
            if not invoices.empty:
                df_invoices[year] = invoices[invoices['Year'] == year].copy().reset_index(drop=True)
            else:
                df_invoices[year] = pd.DataFrame()

            if not credits.empty:
                df_credits[year] = credits[credits['Year'] == year].copy().reset_index(drop=True)
            else:
                df_credits[year] = pd.DataFrame()

        return df_invoices, df_credits

    @staticmethod
    def merge_and_equalize_by_year(  # noqa: PLR0912
        df_invoices: dict[int, pd.DataFrame], df_credits: dict[int, pd.DataFrame]
    ) -> dict[int, pd.DataFrame]:
        """
        Merge invoices and credits DataFrames by year, aligning by Customer.
        For each year, performs an outer merge on 'Customer', filling missing rows with NaN.
        Ensures all yearly DataFrames have the same number of rows by padding with empty rows as needed.

        Args:
            df_invoices (dict[int, pd.DataFrame]): Dict of invoices DataFrames by year.
            df_credits (dict[int, pd.DataFrame]): Dict of credits DataFrames by year.

        Returns:
            dict[int, pd.DataFrame]: Dict of merged and equalized DataFrames by year.
        """
        merged_by_year = {}
        all_customers_set = set()

        # Collect all unique customers across all years
        for year_key in set(df_invoices.keys()).union(df_credits.keys()):
            inv_df = df_invoices.get(year_key, pd.DataFrame())
            cred_df = df_credits.get(year_key, pd.DataFrame())
            if not inv_df.empty and 'Customer' in inv_df.columns:
                all_customers_set.update(inv_df['Customer'].unique())
            if not cred_df.empty and 'Customer' in cred_df.columns:
                all_customers_set.update(cred_df['Customer'].unique())

        all_customers_list = sorted(list(all_customers_set))
        max_rows = 0

        expected_cols = ['Year', 'Customer', 'Amount']

        # Merge and pad per year
        for year_key in set(df_invoices.keys()).union(df_credits.keys()):
            inv = df_invoices.get(year_key, pd.DataFrame())
            cred = df_credits.get(year_key, pd.DataFrame())

            # Standardize DataFrames: ensure 'Customer' is the index and not a column.
            if inv.empty:
                # Create an empty DataFrame with expected columns and 'Customer' as index
                inv = pd.DataFrame(columns=expected_cols).set_index('Customer')
            else:
                # Ensure 'Customer' is the index
                # If 'Customer' is not in the columns, it will raise an error.
                if 'Customer' not in inv.columns:
                    raise ValueError(f"DataFrame de invoices para o ano {year_key} não possui coluna 'Customer'")
                inv = inv.copy().set_index('Customer')

            if cred.empty:
                cred = pd.DataFrame(columns=expected_cols).set_index('Customer')
            else:
                if 'Customer' not in cred.columns:
                    raise ValueError(f"DataFrame de créditos para o ano {year_key} não possui coluna 'Customer'")
                cred = cred.copy().set_index('Customer')

            merged = pd.merge(
                inv, cred, how='outer', left_index=True, right_index=True, suffixes=('_invoice', '_credit')
            )

            merged = merged.reset_index()  # Agora 'Customer' (do índice) se torna uma coluna

            # Ensure all customers are present
            if 'Customer' not in merged.columns:
                if 'index' in merged.columns and merged.index.name is None:  # Common if index was unnamed
                    merged.rename(columns={'index': 'Customer'}, inplace=True)
                else:
                    raise ValueError(
                        (
                            f"Coluna 'Customer' não encontrada após reset_index para o ano {year_key}. "
                            f'Index name era: {merged.index.name if hasattr(merged, "index") else "N/A"}'
                        )
                    )

            merged = merged.set_index('Customer').reindex(all_customers_list).reset_index()

            if 'Year_invoice' in merged.columns:
                merged['Year_invoice'] = merged['Year_invoice'].fillna(year_key)
            if 'Year_credit' in merged.columns:
                merged['Year_credit'] = merged['Year_credit'].fillna(year_key)

            merged_by_year[year_key] = merged
            max_rows = max(max_rows, len(merged))

        # Equalize all DataFrames to have the same number of rows
        for year_k, df_item in merged_by_year.items():
            if len(df_item) < max_rows:
                pad_rows = max_rows - len(df_item)
                empty_padding = pd.DataFrame({col: [pd.NA] * pad_rows for col in df_item.columns})
                merged_by_year[year_k] = pd.concat([df_item, empty_padding], ignore_index=True)

        return merged_by_year

    @staticmethod
    def create_final_report(merged_by_year: dict[int, pd.DataFrame], customers: dict[str, str]) -> pd.DataFrame:
        sorted_years = sorted(merged_by_year.keys())
        first_year = sorted_years[0]

        first_year_df = merged_by_year[first_year]
        customer_info_df = first_year_df[['Customer']].copy()
        customer_info_df['Name'] = customer_info_df['Customer'].map(customers)

        customer_info_df.columns = pd.MultiIndex.from_product([['Info'], customer_info_df.columns])

        value_dfs = []
        for year in sorted_years:
            df_original = merged_by_year.get(year, pd.DataFrame())
            value_df = df_original[['Amount_invoice', 'Amount_credit']]
            value_dfs.append(value_df)

            merged_by_year[year] = df_original

        # Contact only values, create a MultiIndex with years
        yearly_data_df = pd.concat(value_dfs, axis=1, keys=sorted_years)

        # Calculate Balance for each year
        for year in sorted_years:
            invoice = yearly_data_df[(year, 'Amount_invoice')].fillna(0)
            credit = yearly_data_df[(year, 'Amount_credit')].fillna(0)

            yearly_data_df[(year, 'Balance')] = invoice - credit

        columns_order = ['Amount_invoice', 'Amount_credit', 'Balance']

        ordered_columns = [(year, column) for year in sorted_years for column in columns_order]

        yearly_data_df = yearly_data_df[ordered_columns]

        final_df = pd.concat([customer_info_df, yearly_data_df], axis=1)

        return final_df
