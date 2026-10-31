# Documentação

A documentação usa [MkDocs](https://www.mkdocs.org/) com o tema
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) e o plugin
[mkdocstrings](https://mkdocstrings.github.io/) para gerar a referência da API a partir das docstrings.

## Instalar

```bash
uv sync --group docs
# ou
pip install -r requirements-docs.txt
```

## Utilizar

```bash
uv run mkdocs serve            # http://127.0.0.1:8000 com recarregamento automático
uv run mkdocs build --strict   # gera site/ e falha se houver avisos
```

O mkdocstrings lê o código de `src/` por **análise estática** (griffe). Não importa os
módulos, por isso não precisa de `secrets.toml` nem de ligação à base de dados.

## Estrutura

```text
docs/
├── index.md
├── guia/              # instalação, configuração, execução
├── arquitetura/       # camadas, pastas, autenticação, relatórios
├── desenvolvimento/   # fluxo de trabalho, como acrescentar relatórios
├── referencia/        # páginas com diretivas `::: modulo`
└── migracao.md
```

Para documentar um módulo novo, acrescente uma linha `::: gn_dashboard.<modulo>` à página
correspondente em `docs/referencia/`.
