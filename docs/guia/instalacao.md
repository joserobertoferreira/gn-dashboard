# Instalação

## Pré-requisitos

- **Python 3.12** (ver `.python-version`).
- **Microsoft ODBC Driver 17 ou 18 for SQL Server** instalado no sistema.
- Acesso de rede ao servidor SQL Server do Sage X3.
- Recomendado: [uv](https://docs.astral.sh/uv/).

## Com uv (recomendado)

```bash
uv sync                 # dependências da aplicação + grupo dev
uv sync --all-groups    # inclui também as dependências da documentação
```

O `uv sync` instala o próprio projeto em modo editável, o que torna o pacote
`gn_dashboard` importável pelas páginas Streamlit.

## Com pip

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate       # Linux/macOS

pip install -r requirements.txt   # aplicação (inclui `-e .`)
pip install -r requirements-docs.txt   # opcional: documentação
```

!!! warning "O pacote tem de estar instalado"
    O código vive em `src/gn_dashboard`. Se correr a aplicação sem instalar o pacote
    (`pip install -e .` ou `uv sync`), os imports `from gn_dashboard...` falham.

## Ficheiros de dependências

| Ficheiro | Conteúdo | Gerado por |
|---|---|---|
| `pyproject.toml` | Dependências declaradas (fonte de verdade) | manual |
| `uv.lock` | Versões exatas resolvidas | `uv lock` |
| `requirements.txt` | Versões exatas para pip (aplicação) | `uv export --no-dev --no-hashes -o requirements.txt` |
| `requirements-docs.txt` | Versões exatas para pip (MkDocs) | `uv export --only-group docs --no-hashes --no-emit-project -o requirements-docs.txt` |
