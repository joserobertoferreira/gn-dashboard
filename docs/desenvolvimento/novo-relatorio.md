# Adicionar um relatório

Exemplo: um relatório "Vendas por país".

## 1. Repositório (se houver uma entidade nova)

`src/gn_dashboard/repositories/sales_repository.py`

```python
from gn_dashboard.database.query_builder import QueryBuilder
from gn_dashboard.database.session import get_database_manager


class SalesRepository:
    def __init__(self, db=None):
        self.db = db or get_database_manager()

    def totals_by_country(self, year: int) -> list[dict]:
        query = QueryBuilder(self.db)
        result = query.execute_query(
            table=f'{query.schema}.SINVOICE',
            columns=['BPRCRY_0 AS Country', 'SUM(AMTATI_0) AS Amount'],
            where_clauses={'YEAR(ACCDAT_0)': ('=', year)},
            options={'group_by': 'BPRCRY_0', 'order_by': 'BPRCRY_0'},
        )
        return result['data'] if result['status'] == 'success' else []
```

## 2. Serviço

`src/gn_dashboard/services/sales_service.py`, com a regra de negócio e a cache:

```python
import pandas as pd
import streamlit as st

from gn_dashboard.repositories.sales_repository import SalesRepository


class SalesService:
    @staticmethod
    @st.cache_data(ttl=600)
    def totals_by_country(year: int) -> pd.DataFrame:
        return pd.DataFrame(SalesRepository().totals_by_country(year))
```

## 3. Página

`src/gn_dashboard/views/reports/sales_by_country.py`

```python
import streamlit as st

from gn_dashboard.services.sales_service import SalesService
from gn_dashboard.ui.guards import require_authentication

require_authentication()
st.subheader('Vendas por País')
year = st.sidebar.number_input('Ano', value=2025, step=1)
st.dataframe(SalesService.totals_by_country(int(year)), hide_index=True)
```

## 4. Registar em `app.py`

```python
sales_page = st.Page(
    VIEWS_DIR / 'reports' / 'sales_by_country.py',
    title='Vendas por País',
    icon=':material/public:',
)
# ...
'Relatórios': [annual_revenue_page, sales_page],
```

## 5. Testes e documentação

- Acrescente testes em `tests/` para a lógica do serviço.
- Acrescente `::: gn_dashboard.services.sales_service` a `docs/referencia/services.md`.
- Descreva o relatório em `docs/arquitetura/relatorios.md`.
