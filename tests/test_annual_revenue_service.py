import pandas as pd
import pytest

from gn_dashboard.services.annual_revenue_service import AnnualRevenueService


@pytest.fixture
def raw_data():
    invoices = pd.DataFrame({
        'Year': [2024, 2024, 2025],
        'Customer': ['C1', 'C2', 'C1'],
        'Amount': [100.0, 50.0, 80.0],
    })
    credits = pd.DataFrame({'Year': [2025], 'Customer': ['C3'], 'Amount': [10.0]})
    return invoices, credits


def test_split_revenue_by_year(raw_data):
    inv, cred = AnnualRevenueService.split_revenue_by_year(*raw_data, start_year=2024, end_year=2025)
    assert set(inv) == {2024, 2025}
    assert len(inv[2024]) == 2
    assert cred[2024].empty


def test_merge_and_final_report(raw_data):
    inv, cred = AnnualRevenueService.split_revenue_by_year(*raw_data, start_year=2024, end_year=2025)
    merged = AnnualRevenueService.merge_and_equalize_by_year(inv, cred)

    # Todos os anos têm todos os clientes
    assert all(list(df['Customer']) == ['C1', 'C2', 'C3'] for df in merged.values())

    report = AnnualRevenueService.create_final_report(merged, {'C1': 'Cliente 1', 'C3': 'Cliente 3'})
    row_c1 = report[report['Info', 'Customer'] == 'C1'].iloc[0]
    row_c3 = report[report['Info', 'Customer'] == 'C3'].iloc[0]

    assert row_c1['Info', 'Name'] == 'Cliente 1'
    assert row_c1[2024, 'Balance'] == 100.0
    assert row_c3[2025, 'Balance'] == -10.0
