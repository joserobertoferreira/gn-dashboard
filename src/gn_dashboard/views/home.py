"""Página inicial."""

import streamlit as st

st.title('GN - Dashboard')
st.subheader('Home')
st.write(f'Bem-vindo ao GN - Dashboard, {st.session_state.get("user") or ""}!')
