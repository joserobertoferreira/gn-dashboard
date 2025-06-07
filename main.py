import logging

import streamlit as st

from config.logging import setup_logging

st.set_page_config(
    page_title='GN - Dashboard',
    page_icon='https://www.garrafeiranacional.com/media/favicon/default/favicon_2.ico',
    layout='wide',  # Usar layout 'wide' para dashboards
    # initial_sidebar_state='expanded',  # Manter sidebar aberta por padrão
)
st.logo('images/footer-logo.png', size='large', icon_image='images/footer-logo.png')

setup_logging()

logger = logging.getLogger(__name__)

# Initialize the Session State
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None

# Home page
home_page = st.Page('home.py', title='Home', icon=':material/home:', default=True)

# Authentication pages
login_page = st.Page('auth/login.py', title='Login', icon=':material/login:')
reset_page = st.Page('auth/reset.py', title='Reset Password', icon=':material/key:')
logout_page = st.Page('auth/logout.py', title='Logout', icon=':material/logout:')

auth_pages = [reset_page, logout_page]

# Reports pages
annual_revenue_page = st.Page(
    'reports/annual_revenue_per_customer.py',
    title='Receita Anual por Cliente',
    icon=':material/bar_chart:',
)

reports_pages = [annual_revenue_page]

# Define navigation
page_dict = {}

if st.session_state.authenticated:
    logger.info(f'User {st.session_state.user} is authenticated: {st.session_state.authenticated}')

    page_dict['Home'] = [home_page]
    page_dict['Authentication'] = auth_pages
    page_dict['Reports'] = reports_pages
else:
    st.title('GN - Acesso ao Sistema')

    page_dict['Authentication'] = [login_page]

# Execute navigation
pg = st.navigation(page_dict)

pg.run()
