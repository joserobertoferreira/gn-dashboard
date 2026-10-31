"""Permite arrancar a aplicação com `python -m gn_dashboard` ou com o comando `gn-dashboard`."""

import sys
from pathlib import Path


def main() -> None:
    """Executa `streamlit run` sobre `app.py`, passando argumentos extra ao Streamlit."""
    from streamlit.web import cli as stcli  # noqa: PLC0415

    app_path = Path(__file__).resolve().parent / 'app.py'
    sys.argv = ['streamlit', 'run', str(app_path), *sys.argv[1:]]
    sys.exit(stcli.main())


if __name__ == '__main__':
    main()
