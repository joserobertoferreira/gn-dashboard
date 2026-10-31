"""Proteções de acesso às páginas Streamlit."""

import streamlit as st

#: Chaves do `st.session_state` relacionadas com autenticação.
AUTH_SESSION_KEYS = ('authenticated', 'user')


def init_session_state() -> None:
    """Inicializa as chaves de autenticação no `st.session_state`."""
    st.session_state.setdefault('authenticated', False)
    st.session_state.setdefault('user', None)


def is_authenticated() -> bool:
    """Indica se existe um utilizador autenticado na sessão."""
    return bool(st.session_state.get('authenticated', False))


def require_authentication() -> None:
    """Interrompe a página se o utilizador não estiver autenticado.

    A navegação (`app.py`) só mostra a página de login a utilizadores não autenticados;
    esta verificação é uma segunda barreira caso uma página seja aberta diretamente.
    """
    if not is_authenticated():
        st.warning('🔒 Acesso negado. Por favor, faça login para visualizar esta página.')
        st.stop()


def clear_authentication() -> None:
    """Remove os dados de autenticação da sessão."""
    for key in AUTH_SESSION_KEYS:
        st.session_state.pop(key, None)
