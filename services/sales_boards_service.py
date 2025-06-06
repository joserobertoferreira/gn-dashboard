import datetime
import logging
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st

from database.manager import db
from utils.comparison_table_data import equalize_rows

logger = logging.getLogger(__name__)


class SalesBoardsService:
    """
    Service class for handling sales boards data.
    This class is responsible for fetching and processing sales data from the database.
    """

    def __init__(self):
        pass

    @staticmethod
    @st.cache_data(ttl=600)
    def fetch_sales_data(schema: str, publication: str, year: int) -> pd.DataFrame:  # noqa: PLR6301
        """
        Fetches sales data from the database for the specified publication and years.
        This function MUST be adapted with the correct SQL query for your database.
        """

        if not db:  # Verifica se db e seu engine foram inicializados
            st.error('Gerenciador do banco não disponível.')
            logger.error('Gerenciador do banco não disponível.')
            return pd.DataFrame()

        end_date = datetime.date(year, 12, 31).strftime('%Y-%m-%d')
        start_date = datetime.date(year - 1, 1, 1).strftime('%Y-%m-%d')
        logger.info(
            f'Buscar dados de vendas para Pub: {publication}, Ano Anterior: {start_date[:4]}, Ano Atual: {end_date[:4]}'
        )

        query = f"""
        SELECT
            YEAR(a.DISDAT_0) as Year,
            a.NUMEDI_0 as Issue,
            a.DISDAT_0 as Date,
            a.QTYRREC_0 as Supply,
            ((a.QTYREXP_0+ISNULL(CONVERT(int,b.QTY_0),0))-a.QTYRDEV_0) as Sales,
            0 as Unsolds,
            ISNULL(CONVERT(int,c.OUT),0) as Outlet
        FROM {schema}.ZITMINP a WITH (NOLOCK)
        LEFT JOIN (SELECT x.ITMREF_0,SUM(CASE WHEN y.INVTYP_0=2 THEN x.QTY_0*-1 ELSE x.QTY_0 END) AS QTY_0
                FROM {schema}.SINVOICED x WITH (NOLOCK)
                INNER JOIN {schema}.SINVOICE y WITH (NOLOCK) ON y.NUM_0=x.NUM_0
                WHERE x.CPY_0='INP'
                AND x.BPCINV_0 NOT IN (SELECT VALEUR_0 FROM {schema}.ADOVAL WITH (NOLOCK) WHERE PARAM_0='BPCINV')
                GROUP BY x.ITMREF_0) b ON b.ITMREF_0=a.ITMREF_0
        LEFT JOIN (SELECT ITMREF_0,COUNT(1) AS OUT FROM {schema}.ZBPCEST GROUP BY ITMREF_0) c ON c.ITMREF_0=a.ITMREF_0
        WHERE a.DISTVSP_0=2
        AND a.PERNUM_0>1
        AND a.CODPUB_0= ?
        AND a.DISDAT_0 BETWEEN ? AND ?
        ORDER BY a.DISDAT_0,a.NUMEDI_0
        """
        params = (
            publication,
            start_date,
            end_date,
        )

        df = db.run_query(query, params)

        if df.empty:
            logger.warning(f'Nenhum dado retornado do banco para os parâmetros: {params}')
            return pd.DataFrame()

        logger.info(f'Dados brutos recebidos do banco ({len(df)} linhas). Colunas: {df.columns.tolist()}')

        try:
            # df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            # df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

            # Calculate Unsolds column
            df['Unsolds'] = np.where(df['Supply'] > 0, ((df['Supply'] - df['Sales']) / df['Supply']), 0)

        except Exception as e:
            logger.error(f'Erro durante a conversão de tipos de dados: {e}', exc_info=True)
            st.error(f'Erro ao processar os tipos de dados recebidos do banco: {e}')
            return pd.DataFrame()

        if df.empty:
            logger.warning(f'Dados vazios após limpeza/conversão de tipos para os parâmetros: {params}')

        return df

    def calculate_metrics(  # noqa: PLR0914, PLR6301
        self,
        df_prev: pd.DataFrame,
        df_curr: pd.DataFrame,
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
        """
        Process the dataframe to calculate metrics for the specified year.
        Args:
            df (pd.DataFrame): DataFrame containing sales data.
            suffix (str): suffix.
        Returns:
            tuple: Four dictionaries with calculated metrics.
        """

        df = pd.merge(df_prev, df_curr, left_index=True, right_index=True, how='outer', suffixes=('_0', '_1'))

        for suffix in range(2):
            # Calculate totals
            total_supply = df[f'Supply_{suffix}'].sum()
            total_sales = df[f'Sales_{suffix}'].sum()
            total_unsold_perc = np.nan

            if total_supply > 0:
                total_unsold_calc = (total_supply - total_sales) / total_supply
                total_unsold_perc = total_unsold_calc if pd.notnull(total_unsold_calc) else np.nan

            # Calculate averages
            avg_supply = df[f'Supply_{suffix}'].mean()
            avg_sales = df[f'Sales_{suffix}'].mean()
            avg_outlet = df[f'Outlet_{suffix}'].mean()
            avg_unsold_perc = np.nan

            # Check if avg_supply is not NaN and greater than 0 before calculating
            if pd.notnull(avg_supply) and avg_supply > 0:
                # Also check if avg_sales is not NaN for the calculation
                if pd.notnull(avg_sales):
                    avg_unsold_calc = (avg_supply - avg_sales) / avg_supply
                    avg_unsold_perc = avg_unsold_calc if pd.notnull(avg_unsold_calc) else np.nan

            # Prepare the metrics dictionary
            if suffix == 0:
                totals_0 = {
                    'Issue_0': ['Total'],
                    'Date_0': [' '],
                    'Supply_0': int(total_supply),
                    'Sales_0': int(total_sales),
                    'Unsolds_0': total_unsold_perc,
                    'Outlet_0': 0,
                }
                averages_0 = {
                    'Issue_0': ['Average'],
                    'Date_0': [' '],
                    'Supply_0': int(avg_supply),
                    'Sales_0': int(avg_sales),
                    'Unsolds_0': avg_unsold_perc,
                    'Outlet_0': int(avg_outlet),
                }
            else:
                totals_1 = {
                    'Issue_1': ['Total'],
                    'Date_1': [' '],
                    'Supply_1': int(total_supply),
                    'Sales_1': int(total_sales),
                    'Unsolds_1': total_unsold_perc,
                    'Outlet_1': 0,
                }
                averages_1 = {
                    'Issue_1': ['Average'],
                    'Date_1': [' '],
                    'Supply_1': int(avg_supply),
                    'Sales_1': int(avg_sales),
                    'Unsolds_1': avg_unsold_perc,
                    'Outlet_1': int(avg_outlet),
                }

        # # Calculate average for variation columns
        # avg_copies = df['Copies_var'].mean()
        # avg_copies_perc = df['%_var'].mean()

        # copies = {
        #     'Copies_var': int(avg_copies) if pd.notnull(avg_copies) else 0,
        #     '%_var': avg_copies_perc if pd.notnull(avg_copies_perc) else 0.0,
        # }

        return totals_0, averages_0, totals_1, averages_1

    def calculate_differences(self, df_diff: pd.DataFrame, current_year: int) -> pd.DataFrame:  # noqa: PLR6301
        """
        Calculate the differences between two DataFrames.
        Args:
            df_diff (pd.DataFrame): DataFrame
            current_year (int): Current year for comparison.
        Returns:
            pd.DataFrame: DataFrame with differences.
        """

        # Calculate differences
        prev_column = 'Sales_0'
        curr_column = 'Sales_1'

        prev_year_col = (str(current_year - 1), prev_column)
        curr_year_col = (str(current_year), curr_column)
        copies_column = ('Variation', 'Copies_var')
        percent_column = ('Variation', '%_var')

        sales_prev = pd.to_numeric(df_diff[prev_year_col], errors='coerce')
        sales_curr = pd.to_numeric(df_diff[curr_year_col], errors='coerce')

        copies_diff = sales_curr - sales_prev

        df_diff[copies_column] = copies_diff.fillna(0).astype(int)
        df_diff[percent_column] = 0.0

        # Criar uma máscara para as condições de cálculo válidas:
        valid_calculation_mask = sales_prev.notna() & sales_curr.notna() & (sales_prev != 0)

        # Calcular %_var apenas onde a máscara é True e atribuir à coluna de destino correta
        df_diff.loc[valid_calculation_mask, percent_column] = (
            copies_diff[valid_calculation_mask] / sales_prev[valid_calculation_mask]
        )

        # Lidar com inf/-inf e quaisquer NaNs restantes na coluna de destino
        df_diff[percent_column] = df_diff[percent_column].replace([np.inf, -np.inf], 0.0).fillna(0.0)
        return df_diff

    def create_comparison_table(self, df_prev: pd.DataFrame, df_curr: pd.DataFrame, year_current: int) -> pd.DataFrame:  # noqa: PLR0914
        """
        Create a comparison table for the sales data.
        Args:
            df_data (pd.DataFrame): DataFrame containing sales data.
            year_current (int): Current year for comparison.
            Returns:
                df: DataFrames for the previous year and current year.
        """

        df_prev, df_curr = equalize_rows(df1=df_prev, df2=df_curr)

        df_prev = df_prev.drop(columns=['Year'], errors='ignore')
        new_columns = [f'{col}_0' for col in df_prev.columns]
        df_prev.columns = new_columns

        df_curr = df_curr.drop(columns=['Year'], errors='ignore')
        new_columns = [f'{col}_1' for col in df_curr.columns]
        df_curr.columns = new_columns

        # Calculate metrics
        prev_total, prev_average, curr_total, curr_average = self.calculate_metrics(df_prev, df_curr)

        # Adicionar linha de totais
        totals = pd.DataFrame(prev_total).convert_dtypes()
        averages = pd.DataFrame(prev_average).convert_dtypes()

        _df = pd.concat([df_prev, totals, averages], ignore_index=True)
        dic1 = _df.to_dict(orient='dict')

        totals = pd.DataFrame(curr_total).convert_dtypes()
        averages = pd.DataFrame(curr_average).convert_dtypes()

        _df = pd.concat([df_curr, totals, averages], ignore_index=True)
        dic2 = _df.to_dict(orient='dict')

        dic3 = {
            'Copies_var': {i: 0 for i in range(len(dic2['Issue_1']))},
            '%_var': {i: 0.0 for i in range(len(dic2['Issue_1']))},
        }

        data = {
            **{(f'{year_current - 1}', f'{col}'): valores for col, valores in dic1.items()},
            **{(f'{year_current}', f'{col}'): valores for col, valores in dic2.items()},
            **{('Variation', f'{col}'): valores for col, valores in dic3.items()},
        }
        df = pd.DataFrame(data)

        # Calculate differences
        df_calculated = self.calculate_differences(df, current_year=year_current)

        df_calculated = df_calculated.fillna('')

        #        df_calculated.columns = pd.MultiIndex.from_tuples(list(data.keys()), names=['Year', 'Metrics', 'Variation'])

        return df_calculated
