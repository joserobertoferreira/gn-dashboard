"""Página de login."""

import logging

import streamlit as st

from gn_dashboard.services.authentication_service import AuthenticationService
from gn_dashboard.ui.guards import is_authenticated

logger = logging.getLogger(__name__)

if is_authenticated():
    st.success(f'Bem-vindo, {st.session_state.user}!')
    st.info('Já tem sessão iniciada.')
    st.stop()

st.caption('Por favor, indique as suas credenciais para aceder ao sistema.')

with st.form(key='login_form', clear_on_submit=True):
    username_input = st.text_input('Utilizador', placeholder='Código de utilizador')
    password_input = st.text_input('Password', type='password', placeholder='Password')
    login_btn = st.form_submit_button('Login')

if login_btn:
    result = AuthenticationService.login(username=username_input, password=password_input)

    if result.get('username'):
        st.session_state.authenticated = True
        st.session_state.user = result['username']
        logger.info('User %s logged in successfully.', st.session_state.user)
        st.rerun()
    else:
        logger.warning('Login failed for user %s', username_input)
        st.error('Utilizador ou password inválidos.')
