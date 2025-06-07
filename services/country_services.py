import logging

import streamlit as st

from repository.country_repository import CountryRepository

logger = logging.getLogger(__name__)


class CountryService:
    """
    Service class for handling country data.
    """

    def __init__(self):
        pass

    @staticmethod
    @st.cache_data(ttl=600)
    def fetch_countries(country: list[str] | None = None) -> list[str]:
        """
        Fetches a list of countries from the database.

        :param country: Optional list of country codes to filter by.
        :return: List of country names.
        """
        repository = CountryRepository()

        return repository.fetch_countries(country=country)
