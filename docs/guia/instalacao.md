# Instalação

## Pré-requisitos

- **Python 3.12** (ver `.python-version`).
- **Microsoft ODBC Driver 17 ou 18 for SQL Server** instalado no sistema.
- Acesso de rede ao servidor SQL Server do Sage X3.
- Recomendado: [uv](https://docs.astral.sh/uv/).

## Instalar o uv

No Windows, numa consola PowerShell, use o instalador oficial:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

O `uv.exe` fica em `%USERPROFILE%\.local\bin`, que é acrescentado ao `PATH` do
utilizador. Feche e volte a abrir o PowerShell e confirme com:

```powershell
uv --version
```

Alternativas:

```powershell
winget install --id=astral-sh.uv -e   # Windows Server 2022+ / Windows 11
python -m pip install uv              # com um Python já instalado
```

!!! tip "Python 3.12"
    Não é preciso instalar o Python à parte: se a versão pedida em `.python-version`
    não existir no sistema, o `uv sync` descarrega-a. Para a instalar antecipadamente,
    use `uv python install 3.12`.

!!! note "No servidor"
    Basta instalar o `uv` no utilizador que faz as atualizações. O serviço Windows
    (ver [Executar como serviço](executar.md#executar-como-servico-do-windows-nssm))
    arranca com `.venv\Scripts\python.exe` e não usa o `uv`.

## Com uv (recomendado)

```bash
uv sync                 # dependências da aplicação + grupo dev
uv sync --all-groups    # inclui também as dependências da documentação
uv sync --no-dev        # só a aplicação (servidor de produção)
```

O `uv sync` instala o próprio projeto em modo editável, o que torna o pacote
`gn_dashboard` importável pelas páginas Streamlit.

!!! warning "Ambiente virtual existente"
    Se o `.venv` foi criado com `pip` e com outra versão do Python, o `uv sync`
    recria-o. No servidor, pare o serviço (`nssm stop Reports_GN`) antes de
    correr o `uv sync`, para que nenhum ficheiro do `.venv` esteja em uso.

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
