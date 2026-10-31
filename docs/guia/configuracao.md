# Configuração

Toda a configuração sensível é lida de `.streamlit/secrets.toml` através de `st.secrets`
no módulo [`gn_dashboard.core.settings`](../referencia/core.md).

!!! danger "Nunca versionar o `secrets.toml`"
    O ficheiro está no `.gitignore`. Só o modelo `.streamlit/secrets.toml.example` é versionado.

## `secrets.toml`

```toml
[app]
debug = false                      # true => echo das queries SQL no log

[database]
server = "SERVIDOR\\INSTANCIA"
database = "x3"
schema = "GN"                      # schema/pasta Sage X3
username = "utilizador"
password = "password"
driver = "ODBC Driver 17 for SQL Server"
trusted_connection = "no"          # "yes" => autenticação Windows
```

### Chaves

| Secção | Chave | Obrigatória | Descrição |
|---|---|---|---|
| `app` | `debug` | não | Ativa o modo debug. Por omissão `false`. |
| `database` | `server` | sim | Servidor SQL Server (`host` ou `host\instancia`). |
| `database` | `database` | sim | Nome da base de dados. |
| `database` | `schema` | sim | Schema da pasta Sage X3 (usado em todas as tabelas). |
| `database` | `username` / `password` | se `trusted_connection = "no"` | Credenciais SQL. |
| `database` | `driver` | não | Por omissão `ODBC Driver 17 for SQL Server`. |
| `database` | `trusted_connection` | não | `"yes"` para autenticação integrada do Windows. |

### Compatibilidade com a versão 0.1

A secção antiga `[debug] production = true|false` continua a ser aceite **quando `[app] debug`
não existe**, com o significado correto: `debug = not production`.

!!! note "Mudança de comportamento"
    Na versão 0.1, `DEBUG` tomava o valor de `production` (estava invertido). Com
    `production = true`, a v0.1 ligava o *echo* SQL e a v0.2 desliga-o.

## `.streamlit/config.toml`

Configuração do servidor Streamlit (versionada). Atualmente só tem `server.headless = true`.

## Logging

Definido em `gn_dashboard.core.settings` (constantes `LOG_*`). Os ficheiros são escritos em
`logs/` na raiz do projeto:

- `logs/app_info.log`: nível INFO ou superior.
- `logs/app_error.log`: nível ERROR, em formato detalhado (módulo, função, linha).
