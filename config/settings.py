from datetime import date, datetime
from pathlib import Path

import streamlit as st

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Database connection parameters
DATABASE = {
    'SERVER': st.secrets['database'].get('server'),
    'DATABASE': st.secrets['database'].get('database'),
    'SCHEMA': st.secrets['database'].get('schema'),
    'USERNAME': st.secrets['database'].get('username'),
    'PASSWORD': st.secrets['database'].get('password'),
    'DRIVER': st.secrets['database'].get('driver'),
    'TRUSTED_CONNECTION': st.secrets['database'].get('trusted_connection'),
}

# Debug mode
DEBUG = st.secrets['debug'].get('production', True)

# Logging configuration
LOG_DIR = 'logs'
LOG_ROOT_LEVEL = 'DEBUG'
LOG_CONSOLE_LEVEL = 'INFO'
LOG_INFO_FILE_ENABLED = True
LOG_INFO_FILENAME = 'app_info.log'
LOG_INFO_FILE_LEVEL = 'INFO'
LOG_ERROR_FILE_ENABLED = True
LOG_ERROR_FILENAME = 'app_error.log'
LOG_ERROR_FILE_LEVEL = 'ERROR'

# Sage X3 database table settings
DEFAULT_LEGACY_DATE = date(1753, 1, 1)
DEFAULT_LEGACY_DATETIME = datetime(1753, 1, 1)
