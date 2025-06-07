import datetime
import logging

import streamlit as st

from services.annual_revenue_service import AnnualRevenueService

logger = logging.getLogger(__name__)

# --- Verificação de Autenticação ---
if not st.session_state.get('authenticated', False):
    st.warning('🔒 Acesso negado. Por favor, faça login para visualizar esta página.')
    st.stop()


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

# country_options = CountryService().fetch_countries(country=None)

# selected_countries = st.sidebar.multiselect(
#     'Selecione os países (deixe em branco para todos):',
#     options=country_options,
#     default=[],
# )

# --- Report Generate Button and Main Logic ---
if st.sidebar.button('Gerar Relatório', key='generate_report_button'):
    revenue = AnnualRevenueService()

    with st.spinner('Buscar dados...'):
        revenue_invoices = revenue.fetch_revenue_data(start_year=start_year, end_year=end_year, invoice_type=1)
        revenue_credits = revenue.fetch_revenue_data(start_year=start_year, end_year=end_year, invoice_type=2)

    if revenue_invoices.empty and revenue_credits.empty:
        st.error('Nenhum dado encontrado para os parâmetros selecionados.')
    else:
        # Create comparison tables
        with st.spinner('Montar visualização...'):
            df_invoices = {}
            df_credits = {}

            for year in range(start_year, end_year + 1):
                df_invoices[year] = revenue_invoices.loc[year].copy().reset_index(drop=True)

        print(f'DataFrame de faturas: {df_invoices}')

        st.write(df_invoices)
        # st.dataframe(df_invoices, use_container_width=True)
