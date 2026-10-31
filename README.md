# GN Dashboard

Dashboard [Streamlit](https://streamlit.io) com relatórios sobre a base de dados **Sage X3**
(SQL Server) da Garrafeira Nacional.

## Arranque rápido

```bash
# 1. Dependências (inclui o pacote gn_dashboard em modo editável)
uv sync                       # ou: pip install -r requirements.txt

# 2. Configuração
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # e preencher

# 3. Executar (a partir da raiz do projeto)
uv run streamlit run src/gn_dashboard/app.py                 # ou: uv run gn-dashboard
```

Requisitos: Python 3.12 e Microsoft ODBC Driver 17/18 for SQL Server.

## Estrutura

```text
src/gn_dashboard/
├── app.py           # entrypoint + navegação
├── core/            # settings, logging, enums Sage X3
├── database/        # engine/sessões, QueryBuilder, ligação
├── models/          # ORM SQLAlchemy (AUTILIS, TABCOUNTRY)
├── repositories/    # acesso a dados
├── services/        # regras de negócio
├── ui/              # guards de autenticação, config. de tabelas
├── utils/           # conversões, pandas
└── views/           # páginas Streamlit (home, auth, reports)
assets/images/       # logótipos
docs/                # documentação MkDocs
tests/               # pytest
```

## Desenvolvimento

| Tarefa | Comando |
|---|---|
| Testes | `uv run pytest` |
| Lint / formatação | `uv run ruff check src tests` / `uv run ruff format src tests` |
| Documentação | `uv run mkdocs serve` (instalar com `uv sync --group docs` ou `pip install -r requirements-docs.txt`) |
| Atualizar requirements | `uv export --no-dev --no-hashes -o requirements.txt` e `uv export --only-group docs --no-hashes --no-emit-project -o requirements-docs.txt` |

A documentação completa (instalação, configuração, arquitetura, referência da API e notas
de migração da versão 0.1) está em `docs/`. Para a ver, corra `uv run mkdocs serve`.
