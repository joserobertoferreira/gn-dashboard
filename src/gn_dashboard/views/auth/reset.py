"""Página de alteração de password do utilizador autenticado."""

import logging

import streamlit as st

from gn_dashboard.services.authentication_service import AuthenticationService
from gn_dashboard.ui.guards import require_authentication

logger = logging.getLogger(__name__)

MIN_PASSWORD_LENGTH = 8

st.title('Alterar Password')
require_authentication()

with st.form(key='change_password_form', clear_on_submit=True):
    current_password = st.text_input('Password atual', type='password')
    new_password = st.text_input('Nova password', type='password')
    confirm_password = st.text_input('Confirmar nova password', type='password')
    submit = st.form_submit_button('Alterar')

if submit:
    if len(new_password) < MIN_PASSWORD_LENGTH:
        st.error(f'A nova password deve ter pelo menos {MIN_PASSWORD_LENGTH} caracteres.')
    elif new_password != confirm_password:
        st.error('As passwords não coincidem.')
    elif AuthenticationService.change_password(st.session_state.user, current_password, new_password):
        logger.info('Password alterada para o utilizador %s.', st.session_state.user)
        st.success('Password alterada com sucesso.')
    else:
        st.error('Não foi possível alterar a password. Verifique a password atual.')
