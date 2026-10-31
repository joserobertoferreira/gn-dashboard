import pytest

from gn_dashboard.ui.tables import adjust_table_height, config_columns_to_annual_revenue


@pytest.mark.parametrize(('rows', 'expected'), [(0, 200), (10, 300), (1000, 633)])
def test_adjust_table_height(rows, expected):
    assert adjust_table_height(rows) == expected


def test_config_columns_keys():
    expected = {'Customer', 'Name', 'Amount_invoice', 'Amount_credit', 'Balance'}
    assert set(config_columns_to_annual_revenue()) == expected
