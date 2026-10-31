"""Ponto de entrada da aplicação Streamlit.

Executar a partir da raiz do projeto:

```bash
streamlit run src/gn_dashboard/app.py
# ou
gn-dashboard
```
"""

import logging

import streamlit as st

from gn_dashboard.core.logging_config import setup_logging
from gn_dashboard.core.settings import IMAGES_DIR, VIEWS_DIR
from gn_dashboard.ui.guards import init_session_state, is_authenticated

st.set_page_config(
    page_title='GN - Dashboard',
    page_icon=str(IMAGES_DIR / 'favicon.ico'),
    layout='wide',
)
st.logo(str(IMAGES_DIR / 'footer-logo.png'), size='large', icon_image=str(IMAGES_DIR / 'footer-logo.png'))

setup_logging()
logger = logging.getLogger(__name__)

init_session_state()

# --- Páginas ---
home_page = st.Page(VIEWS_DIR / 'home.py', title='Home', icon=':material/home:', default=True)

login_page = st.Page(VIEWS_DIR / 'auth' / 'login.py', title='Login', icon=':material/login:')
reset_page = st.Page(VIEWS_DIR / 'auth' / 'reset.py', title='Alterar Password', icon=':material/key:')
logout_page = st.Page(VIEWS_DIR / 'auth' / 'logout.py', title='Logout', icon=':material/logout:')

annual_revenue_page = st.Page(
    VIEWS_DIR / 'reports' / 'annual_revenue_per_customer.py',
    title='Receita Anual por Cliente',
    icon=':material/bar_chart:',
)

# --- Navegação ---
if is_authenticated():
    logger.debug('User %s is authenticated.', st.session_state.user)
    page_dict = {
        'Home': [home_page],
        'Autenticação': [reset_page, logout_page],
        'Relatórios': [annual_revenue_page],
    }
else:
    st.title('GN - Acesso ao Sistema')
    page_dict = {'Autenticação': [login_page]}

st.navigation(page_dict).run()
