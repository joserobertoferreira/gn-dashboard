"""Relatório: receita anual por cliente (faturas, notas de crédito e saldo por ano)."""

import datetime
import logging

import streamlit as st

from gn_dashboard.core.enums import Chapter645
from gn_dashboard.services.annual_revenue_service import AnnualRevenueService
from gn_dashboard.services.customer_service import CustomerService
from gn_dashboard.ui.guards import require_authentication
from gn_dashboard.ui.tables import adjust_table_height, config_columns_to_annual_revenue

logger = logging.getLogger(__name__)

require_authentication()


# --- Page configuration ---
st.subheader('📊 Receita Anual por Cliente')

# --- Inputs ---
st.sidebar.header('Filtros do Relatório')

current_year = datetime.date.today().year
min_years = 3
max_years = 5

years_to_display = st.sidebar.slider(
    'Selecione o número de anos para análise:',
    min_value=min_years,
    max_value=max_years,
    step=1,
)

end_year = current_year
start_year = end_year - (years_to_display - 1)
selected_years = list(range(start_year, end_year + 1))

st.markdown(f'Este relatório mostra a receita anual por cliente para os anos {", ".join(map(str, selected_years))}.')

# --- Report Generate Button and Main Logic ---
if st.sidebar.button('Gerar Relatório', key='generate_report_button'):
    revenue = AnnualRevenueService()
    customer = CustomerService()

    with st.spinner('A obter a lista de clientes...'):
        customers = customer.fetch_raw_customers(filter=None)

    with st.spinner('A obter dados...'):
        revenue_invoices = revenue.fetch_revenue_data(
            start_year=start_year, end_year=end_year, invoice_type=Chapter645.INVOICE
        )
        revenue_credits = revenue.fetch_revenue_data(
            start_year=start_year, end_year=end_year, invoice_type=Chapter645.CREDIT_NOTE
        )

    if revenue_invoices.empty and revenue_credits.empty:
        st.info('Nenhum dado encontrado para os parâmetros selecionados.')
    else:
        # Create comparison tables
        with st.spinner('A preparar a visualização...'):
            # Create a DataFrame for each year with the corresponding invoices and credits
            df_invoices, df_credits = revenue.split_revenue_by_year(
                invoices=revenue_invoices, credits=revenue_credits, start_year=start_year, end_year=end_year
            )

            # Leave both DataFrames with same number of rows
            df_equalized = revenue.merge_and_equalize_by_year(df_invoices, df_credits)

        if len(df_equalized) > 0:
            df_show = revenue.create_final_report(df_equalized, customers)

            if not df_show.empty:
                config_columns = config_columns_to_annual_revenue()

                # Adjust table height based on number of rows
                table_height = adjust_table_height(len(df_show))

                st.dataframe(
                    df_show,
                    hide_index=True,
                    height=table_height,
                    column_config=config_columns,
                    use_container_width=True,
                )
            else:
                st.info('Nenhum dado encontrado para os parâmetros selecionados.')
        else:
            st.info('Nenhum dado encontrado para os parâmetros selecionados.')
