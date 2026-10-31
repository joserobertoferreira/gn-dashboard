# Migração 0.1 → 0.2

A versão 0.1 está preservada, intacta e com histórico git, em `D:\Python\Sage\GN\dashboard_old`.
A versão 0.2 foi feita no branch `refactor/structure`. Os ficheiros foram movidos com
`git mv`, por isso o histórico de cada um continua acessível com `git log --follow`.

## Mapeamento de ficheiros

| 0.1 | 0.2 |
|---|---|
| `main.py` | `src/gn_dashboard/app.py` |
| `home.py` | `src/gn_dashboard/views/home.py` |
| `auth/login.py`, `logout.py`, `reset.py` | `src/gn_dashboard/views/auth/` |
| `reports/annual_revenue_per_customer.py` | `src/gn_dashboard/views/reports/` |
| `config/settings.py` | `src/gn_dashboard/core/settings.py` |
| `config/logging.py` | `src/gn_dashboard/core/logging_config.py` |
| `utils/local_menus.py` + `TaxLevel`/`MULTI_PAYMENTS` | `src/gn_dashboard/core/enums.py` |
| `database/database.py` | `src/gn_dashboard/database/session.py` |
| `database/database_core.py` (`DatabaseCoreManager`) | `src/gn_dashboard/database/query_builder.py` (`QueryBuilder`; o nome antigo é mantido como alias) |
| `utils/generics.py` (`Generics.build_connection_string`) | `src/gn_dashboard/database/connection.py` (funções) |
| `repository/` | `src/gn_dashboard/repositories/` |
| `services/authentication.py` | `src/gn_dashboard/services/authentication_service.py` |
| `services/country_services.py` | `src/gn_dashboard/services/country_service.py` |
| `utils/comparison_table_data.py` | `ui/tables.py` (Streamlit) + `utils/dataframes.py` (pandas) |
| `images/` | `assets/images/` |
| `.env.exemple` | substituído por `.streamlit/secrets.toml.example` |

## Bugs corrigidos

| # | Problema na 0.1 | Correção |
|---|---|---|
| 1 | `services/user_service.py` importava módulos inexistentes (`database.manager`, `pydantic`, `User`, `UserUpdate`) e não podia ser importado. | Reescrito sobre o `UserRepository`. |
| 2 | `logout.py` e `reset.py` faziam `st.switch_page('pages/login.py')`, um ficheiro que não existe. | Passam a usar `require_authentication()`. |
| 3 | Com `table_alias`, o `execute_query` gerava `FROM alias AS alias`. | Passa a gerar `FROM tabela AS alias`. |
| 4 | `Countries` tinha o schema `'TGN'` fixo no código. | O schema vem sempre da configuração (metadata). |
| 5 | `CountryRepository`/`CustomerRepository` passavam `order_by` fora de `options`, pelo que era ignorado. | Movido para `options`. |
| 6 | `Chapter1.YES` (= 2) era usado como "comprimento 2" nas validações de SQL. | Substituído por uma constante própria. |
| 7 | `DEBUG = secrets['debug']['production']`, com o significado invertido. | `[app] debug`, ou `not production` (ver [Configuração](guia/configuracao.md)). |
| 8 | A ligação à base de dados era criada no import e `settings.py` rebentava sem `secrets.toml`. | Ligação lazy (`get_database_manager()`) e secrets opcionais no import. |
| 9 | `setup_logging()` reconfigurava os handlers em cada rerun do Streamlit. | Configura apenas uma vez por processo. |
| 10 | Os caminhos de imagens e logs eram relativos ao diretório atual. | Caminhos absolutos a partir de `BASE_DIR`. |
| 11 | `trusted_connection` era ignorado. | Suportado (`Trusted_Connection=yes`, sem credenciais). |
| 12 | Os repositórios chamavam `st.error` (UI na camada de dados). | Removido; só fazem logging. |
| 13 | `fillna` em colunas `object` gerava `FutureWarning` do pandas. | Conversão numérica explícita. |
| 14 | `create_final_report` alterava o dicionário recebido. | Já não altera. |

## Outras alterações

- **Página "Reset Password"**: deixou de ser uma página vazia e passou a "Alterar Password",
  com um formulário funcional (password atual, nova password e confirmação).
- **Etiquetas da tabela de receita**: "Total / Total / Saldo" passaram a "Faturas / Notas de
  crédito / Saldo", com 2 casas decimais.
- **Textos da interface** revistos para português de Portugal.
- **Favicon local** (`assets/images/favicon.ico`) em vez do URL remoto.
- **Dependências**: `pandas` passou a ser declarado explicitamente; `python-decouple` foi
  removido (não era usado); `sqlacodegen` passou para o grupo `dev`; foram criados os grupos
  `dev` (pytest, ruff) e `docs` (mkdocs).
- **Testes** com pytest em `tests/`.
- **Comando `gn-dashboard`** para arrancar a aplicação.

## Ações necessárias

1. Recriar o ambiente: `uv sync` (ou `pip install -r requirements.txt`).
2. Rever `.streamlit/secrets.toml`: acrescentar `[app] debug = false|true` (opcional).
3. Arrancar com `uv run streamlit run src/gn_dashboard/app.py` (deixou de ser `streamlit run main.py`).
4. Testar o login e o relatório com a base de dados real.
