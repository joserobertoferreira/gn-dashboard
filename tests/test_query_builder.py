import pytest

from gn_dashboard.database.condition import Condition
from gn_dashboard.database.query_builder import QueryBuilder


def test_requires_db_manager():
    with pytest.raises(ValueError, match='DatabaseManager'):
        QueryBuilder(db_manager=None)


def test_build_where_empty():
    assert QueryBuilder.build_where(None) == ('', {})


def test_build_where_equals_and_in():
    sql, params = QueryBuilder.build_where({'t.id': ('=', 1), 'status': ('in', ['A', ' B '])})
    assert sql == 't.id = :where_tid_0 AND status IN (:where_status_1_in_0, :where_status_1_in_1)'
    assert params == {'where_tid_0': 1, 'where_status_1_in_0': 'A', 'where_status_1_in_1': 'B'}


def test_build_where_empty_in_is_false():
    sql, params = QueryBuilder.build_where({'x': ('IN', [])})
    assert sql == '1 = 0'
    assert params == {}


def test_build_where_between_with_condition_object():
    sql, params = QueryBuilder.build_where({'YEAR(ACCDAT_0)': Condition('BETWEEN', (2023, 2025))})
    assert sql == 'YEAR(ACCDAT_0) BETWEEN :where_YEARACCDAT0_0_start AND :where_YEARACCDAT0_0_end'
    assert params == {'where_YEARACCDAT0_0_start': 2023, 'where_YEARACCDAT0_0_end': 2025}


def test_build_where_is_null_has_no_params():
    assert QueryBuilder.build_where({'x': ('IS NULL', None)}) == ('x IS NULL', {})


@pytest.mark.parametrize('bad', [('IN', 'abc'), ('BETWEEN', (1,)), 'not-a-condition'])
def test_build_where_invalid(bad):
    with pytest.raises(ValueError, match='column x'):
        QueryBuilder.build_where({'x': bad})


def test_build_select_uses_table_name_with_alias(query_builder):
    sql, _ = query_builder.build_select(table='GN.SINVOICE', table_alias='s', columns=['s.NUM_0'])
    assert 'FROM GN.SINVOICE AS s' in sql


def test_build_select_full(query_builder):
    sql, params = query_builder.build_select(
        table='GN.BPCUSTOMER',
        columns=['BPCNUM_0 AS code', {'expression': 'COUNT(*)', 'alias': 'total'}, {'column': 'BPCNAM_0'}],
        joins=[{'type': 'left', 'table': 'GN.X', 'alias': 'x', 'on': 'x.a = BPCNUM_0'}],
        where_clauses={'BPCNUM_0': ('=', 'C1')},
        options={'group_by': ['BPCNUM_0', 'BPCNAM_0'], 'order_by': 'BPCNUM_0'},
        limit=10,
    )
    assert sql == (
        'SELECT TOP 10 BPCNUM_0 AS code, COUNT(*) AS total, BPCNAM_0 FROM GN.BPCUSTOMER '
        'LEFT JOIN GN.X AS x ON x.a = BPCNUM_0 WHERE BPCNUM_0 = :where_BPCNUM0_0 '
        'GROUP BY BPCNUM_0, BPCNAM_0 ORDER BY BPCNUM_0'
    )
    assert params == {'where_BPCNUM0_0': 'C1'}


def test_build_select_defaults_to_star(query_builder):
    sql, params = query_builder.build_select(table='T')
    assert sql == 'SELECT * FROM T'
    assert params == {}


def test_execute_query_without_table_returns_error(query_builder):
    assert query_builder.execute_query()['status'] == 'error'


def test_update_and_delete_require_where(query_builder):
    assert query_builder.execute_update('T', {'a': 1}, {})['status'] == 'error'
    assert query_builder.execute_delete('T', {})['status'] == 'error'
