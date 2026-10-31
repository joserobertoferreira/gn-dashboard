# Estrutura de pastas

```text
dashboard/
├── .streamlit/
│   ├── config.toml               # configuração do servidor Streamlit (versionado)
│   ├── secrets.toml              # credenciais (NÃO versionado)
│   └── secrets.toml.example      # modelo
├── assets/
│   └── images/                   # logótipos e favicon
├── docs/                         # documentação MkDocs
├── logs/                         # logs da aplicação (não versionado)
├── src/
│   └── gn_dashboard/
│       ├── __init__.py
│       ├── __main__.py           # `python -m gn_dashboard` / comando `gn-dashboard`
│       ├── app.py                # entrypoint Streamlit + navegação
│       ├── core/
│       │   ├── settings.py       # secrets, caminhos, constantes
│       │   ├── logging_config.py
│       │   └── enums.py          # menus locais Sage X3 (Chapter1, Chapter645, ...)
│       ├── database/
│       │   ├── base.py           # DeclarativeBase com schema
│       │   ├── connection.py     # URL de ligação pyodbc
│       │   ├── session.py        # DatabaseManager + get_database_manager()
│       │   ├── query_builder.py  # QueryBuilder (SQL parametrizado)
│       │   └── condition.py
│       ├── models/               # ORM: Users, Countries, mixins
│       ├── repositories/         # UserRepository, CustomerRepository, CountryRepository
│       ├── services/             # AuthenticationService, AnnualRevenueService, ...
│       ├── ui/
│       │   ├── guards.py         # require_authentication(), sessão
│       │   └── tables.py         # column_config e altura das tabelas
│       ├── utils/                # conversões, utilitários pandas
│       └── views/                # páginas Streamlit (st.Page)
│           ├── home.py
│           ├── auth/             # login, logout, alterar password
│           └── reports/          # um ficheiro por relatório
├── tests/                        # pytest
├── mkdocs.yml
├── pyproject.toml
├── uv.lock
├── requirements.txt
├── requirements-docs.txt
└── README.md
```

## Porquê `src/`?

- Os testes e a documentação importam o pacote **instalado**, e não ficheiros soltos da raiz.
- Não há colisões de nomes genéricos (`config`, `utils`, `database`) com outros pacotes.
- A raiz fica só com ficheiros de projeto.

## Porquê `views/` e não `pages/`?

O Streamlit trata uma pasta `pages/` ao lado do script principal como navegação automática
(API antiga). Como a navegação é definida explicitamente com `st.navigation` em `app.py`,
o nome `views/` evita qualquer ambiguidade.
