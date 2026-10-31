"""Página de logout."""

import logging

import streamlit as st

from gn_dashboard.ui.guards import clear_authentication, require_authentication

logger = logging.getLogger(__name__)

st.title('Logout')
require_authentication()

st.warning('Tem a certeza que pretende sair?')

if st.button('Logout'):
    user_logout = st.session_state.get('user', 'Unknown user')
    clear_authentication()
    logger.info('User %s logged out.', user_logout)
    st.rerun()
