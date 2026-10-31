# Fluxo de trabalho

## Comandos

| Tarefa | Comando |
|---|---|
| Instalar tudo | `uv sync --all-groups` |
| Executar a app | `uv run streamlit run src/gn_dashboard/app.py` |
| Testes | `uv run pytest` |
| Lint | `uv run ruff check src tests` |
| Formatar | `uv run ruff format src tests` |
| Documentação (servidor local) | `uv run mkdocs serve` |
| Documentação (build) | `uv run mkdocs build --strict` |
| Atualizar requirements | ver [Instalação](../guia/instalacao.md#ficheiros-de-dependencias) |

## Convenções

- **Imports absolutos** a partir do pacote: `from gn_dashboard.services... import ...`.
- **Docstrings em estilo Google** (`Args:`, `Returns:`, `Raises:`), em português.
  São a fonte da [Referência da API](../referencia/index.md).
- **Logging** com `logger = logging.getLogger(__name__)` e formatação lazy
  (`logger.info('x=%s', x)`), nunca `print`.
- **Strings** com aspas simples e linhas até 120 caracteres (ruff).
- Lógica nova vai para `services`/`repositories`, de forma a poder ser testada sem Streamlit.

## Testes

Os testes ficam em `tests/` e não precisam de base de dados: o `QueryBuilder` é testado
através de `build_select()`/`build_where()`, e os serviços pandas com DataFrames de exemplo.
A fixture `query_builder` (em `tests/conftest.py`) fornece um `QueryBuilder` com um
gestor de base de dados falso.

Para validar as páginas sem browser pode usar o `streamlit.testing.v1.AppTest`:

```python
from streamlit.testing.v1 import AppTest

at = AppTest.from_file('src/gn_dashboard/app.py').run()
assert not at.exception
```
