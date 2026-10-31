from gn_dashboard.database.connection import build_connection_string, check_odbc_driver

BASE = {
    'SERVER': 'srv',
    'DATABASE': 'x3',
    'USERNAME': 'u',
    'PASSWORD': 'secret',
    'DRIVER': 'ODBC Driver 17 for SQL Server',
}


def test_returns_none_when_incomplete():
    assert build_connection_string({'SERVER': None, 'DATABASE': 'x3'}) is None


def test_sql_authentication():
    url = build_connection_string({**BASE, 'TRUSTED_CONNECTION': 'no'})
    assert url.username == 'u'
    assert url.password == 'secret'
    assert 'Trusted_Connection' not in url.query
    assert 'secret' not in url.render_as_string(hide_password=True)


def test_trusted_connection_ignores_credentials():
    url = build_connection_string({**BASE, 'TRUSTED_CONNECTION': 'yes'})
    assert url.username is None
    assert url.query['Trusted_Connection'] == 'yes'


def test_check_odbc_driver():
    assert check_odbc_driver('ODBC Driver 18 for SQL Server') is None
    assert check_odbc_driver('SQL Server') is not None
