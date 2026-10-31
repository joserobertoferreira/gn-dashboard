"""Serviço de países."""

import logging

import streamlit as st

from gn_dashboard.repositories.country_repository import CountryRepository

logger = logging.getLogger(__name__)


class CountryService:
    """Serviço para dados de países."""

    @staticmethod
    @st.cache_data(ttl=600)
    def fetch_countries(country: list[str] | None = None) -> list[str]:
        """Devolve as descrições dos países (resultado em cache durante 10 minutos).

        Args:
            country: Lista opcional de códigos de país para filtrar.

        Returns:
            Lista de descrições de países.
        """
        return CountryRepository().fetch_countries(country=country)
