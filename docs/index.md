# GN Dashboard

O **GN Dashboard** é uma aplicação [Streamlit](https://streamlit.io) com relatórios de gestão
construídos sobre a base de dados **Sage X3** (SQL Server) da Garrafeira Nacional.

<div class="grid cards" markdown>

- :material-rocket-launch: **[Instalação](guia/instalacao.md)**: preparar o ambiente e as dependências.
- :material-cog: **[Configuração](guia/configuracao.md)**: ligação à base de dados e secrets.
- :material-sitemap: **[Arquitetura](arquitetura/index.md)**: camadas, fluxo de dados e estrutura de pastas.
- :material-code-braces: **[Referência da API](referencia/index.md)**: documentação gerada a partir do código.

</div>

## Funcionalidades

| Área | Descrição |
|---|---|
| Autenticação | Login com os utilizadores do Sage X3 (`AUTILIS`), passwords com hash Argon2, alteração de password e logout. |
| Receita anual por cliente | Faturas, notas de crédito e saldo por cliente, para os últimos 3 a 5 anos. |

## Arranque rápido

```bash
uv sync                                  # instala dependências e o pacote gn_dashboard
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # e preencher
uv run streamlit run src/gn_dashboard/app.py
```

!!! info "Versão anterior"
    A versão 0.1 do projeto (com `main.py` e `home.py` na raiz) ficou preservada em
    `D:\Python\Sage\GN\dashboard_old`. Ver [Migração 0.1 → 0.2](migracao.md).
