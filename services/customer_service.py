import logging

import streamlit as st

from repository.customer_repository import CustomerRepository

logger = logging.getLogger(__name__)


class CustomerService:
    """
    Service class for handling customer data.
    """

    def __init__(self):
        pass

    @staticmethod
    @st.cache_data(ttl=600)
    def fetch_raw_customers(filter: list[str] | None = None) -> dict[str, str]:
        """
        Fetches a list of customers from the database.

        :param filter: Optional list of customer codes to filter by.
        :return: dictionary of customer codes and names.
        """
        repository = CustomerRepository()

        customers = repository.fetch_raw_customers(filter=filter)

        if not customers:
            logger.warning('Nenhum cliente encontrado.')
            return {}

        return_dict = {customer['code']: customer['name'] for customer in customers}

        return return_dict
