"""Serviço de clientes."""

import logging

import streamlit as st

from gn_dashboard.repositories.customer_repository import CustomerRepository

logger = logging.getLogger(__name__)


class CustomerService:
    """Serviço para dados de clientes."""

    @staticmethod
    @st.cache_data(ttl=600)
    def fetch_raw_customers(filter: list[str] | None = None) -> dict[str, str]:  # noqa: A002
        """Devolve os clientes como dicionário (resultado em cache durante 10 minutos).

        Args:
            filter: Lista opcional de códigos de cliente para filtrar.

        Returns:
            Dicionário `código -> nome`.
        """
        customers = CustomerRepository().fetch_raw_customers(filter=filter)
        if not customers:
            logger.warning('Nenhum cliente encontrado.')
            return {}
        return {customer['code']: customer['name'] for customer in customers}
