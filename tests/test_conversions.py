from datetime import date, datetime
from decimal import Decimal

from gn_dashboard.core.settings import DEFAULT_LEGACY_DATETIME
from gn_dashboard.utils.conversions import Conversions


def test_convert_value_strips_strings_recursively():
    assert Conversions.convert_value(['  a ', 1]) == ['a', 1]


def test_convert_decimal_non_normal_becomes_zero():
    assert Conversions.convert_value(Decimal('0')) == Decimal(0)


def test_convert_to_date():
    assert Conversions.convert_to_date('2025-06-08') == date(2025, 6, 8)
    assert Conversions.convert_to_date('xx', default=True) == date(1753, 1, 1)
    assert Conversions.convert_to_date('xx') is None


def test_convert_string_to_datetime():
    assert Conversions.convert_string_to_datetime(None) == DEFAULT_LEGACY_DATETIME
    assert Conversions.convert_string_to_datetime('2025-01-02T03:04:05') == datetime(2025, 1, 2, 3, 4, 5)


def test_is_number():
    assert Conversions.is_number('3') == 'integer'
    assert Conversions.is_number('3.5') == 'decimal'
    assert Conversions.is_number('x') is None
