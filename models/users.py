import datetime
import decimal
from typing import List, Optional

from sqlalchemy import (
    DateTime,
    Index,
    Integer,
    Numeric,
    PrimaryKeyConstraint,
    SmallInteger,
    Unicode,
    inspect,
    text,
)
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from config.settings import DATABASE, DEFAULT_LEGACY_DATETIME
from database.base import Base

from .generics_mixins import ArrayColumnMixin
from .mixins import AuditMixin, PrimaryKeyMixin


class Users(Base, AuditMixin, PrimaryKeyMixin, ArrayColumnMixin):
    __tablename__ = 'AUTILIS'
    __table_args__ = (
        PrimaryKeyConstraint('ROWID', name='AUTILIS_ROWID'),
        Index('AUTILIS_CODUSR', 'USR_0', unique=True),
        Index('AUTILIS_LOGIN', 'LOGIN_0'),
        {'schema': f'{DATABASE["SCHEMA"]}'},
    )

    name: Mapped[str] = mapped_column('NOMUSR_0', Unicode(30, 'Latin1_General_BIN2'), default=text("''"))
    username: Mapped[str] = mapped_column('USR_0', Unicode(5, 'Latin1_General_BIN2'), default=text("''"))
    login: Mapped[str] = mapped_column('LOGIN_0', Unicode(20, 'Latin1_General_BIN2'), default=text("''"))
    password: Mapped[str] = mapped_column('YPWDHASH_0', Unicode(128, 'Latin1_General_BIN2'), default=text("''"))
    email: Mapped[str] = mapped_column('ADDEML_0', Unicode(80, 'Latin1_General_BIN2'), default=text("''"))

    PWDBI_0: Mapped[str] = mapped_column(Unicode(24, 'Latin1_General_BIN2'), default=text("''"))
    PASSE_0: Mapped[str] = mapped_column(Unicode(10, 'Latin1_General_BIN2'), default=text("''"))
    DATCONN_0: Mapped[datetime.datetime] = mapped_column(DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'"))
    DECTIME_0: Mapped[int] = mapped_column(Integer, default=text('((0))'))
    DIFIMP_0: Mapped[int] = mapped_column(TINYINT, default=text('((0))'))
    ENAFLG_0: Mapped[int] = mapped_column(TINYINT, default=text('((0))'))
    FAX_0: Mapped[str] = mapped_column(Unicode(40, 'Latin1_General_BIN2'), default=text("''"))
    BPRNUM_0: Mapped[str] = mapped_column(Unicode(10, 'Latin1_General_BIN2'), default=text("''"))
    NBRCON_0: Mapped[int] = mapped_column(SmallInteger, default=text('((0))'))
    PASSDAT_0: Mapped[datetime.datetime] = mapped_column(DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'"))
    TELEP_0: Mapped[str] = mapped_column(Unicode(40, 'Latin1_General_BIN2'), default=text("''"))
    TIMCONN_0: Mapped[str] = mapped_column(Unicode(10, 'Latin1_General_BIN2'), default=text("''"))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='CHEF',
        property_name='chef',
        count=20,
        column_type=Unicode,
        column_args=(35, 'Latin1_General_BIN2'),
        python_type=str,
        default=text("''"),
    )

    chefs: Mapped[List[Optional[str]]] = _properties  # type: ignore

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    CODMET_0: Mapped[str] = mapped_column(Unicode(4, 'Latin1_General_BIN2'), default=text("''"))
    PRFMEN_0: Mapped[str] = mapped_column(Unicode(5, 'Latin1_General_BIN2'), default=text("''"))
    PRFFCT_0: Mapped[str] = mapped_column(Unicode(5, 'Latin1_General_BIN2'), default=text("''"))
    USRBI_0: Mapped[str] = mapped_column(Unicode(5, 'Latin1_General_BIN2'), default=text("''"))
    NBFNC_0: Mapped[int] = mapped_column(SmallInteger, default=text('((0))'))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='FNCCOD',
        property_name='function_code',
        count=8,
        column_type=Unicode,
        column_args=(12, 'Latin1_General_BIN2'),
        python_type=str,
        default=text("''"),
    )

    function_codes: Mapped[List[Optional[str]]] = _properties  # type: ignore

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='FNCPAR',
        property_name='function_parameter',
        count=8,
        column_type=Unicode,
        column_args=(10, 'Latin1_General_BIN2'),
        python_type=str,
        default=text("''"),
    )

    function_parameters: Mapped[List[Optional[str]]] = _properties  # type: ignore

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    ALLACS_0: Mapped[int] = mapped_column(TINYINT, default=text('((0))'))
    USREXT_0: Mapped[int] = mapped_column(TINYINT, default=text('((0))'))
    CHGDAT_0: Mapped[int] = mapped_column(TINYINT, default=text('((0))'))
    REPNUM_0: Mapped[str] = mapped_column(Unicode(10, 'Latin1_General_BIN2'), default=text("''"))
    USRCONNECT_0: Mapped[int] = mapped_column(TINYINT, default=text('((0))'))
    USRCONXTD_0: Mapped[int] = mapped_column(TINYINT, default=text('((0))'))
    CODADRDFT_0: Mapped[str] = mapped_column(Unicode(5, 'Latin1_General_BIN2'), default=text("''"))
    CODRIBDFT_0: Mapped[str] = mapped_column(Unicode(30, 'Latin1_General_BIN2'), default=text("''"))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='PRTDEF',
        property_name='printer_definition',
        count=10,
        column_type=Unicode,
        column_args=(10, 'Latin1_General_BIN2'),
        python_type=str,
        default=text("''"),
    )

    printers_definition: Mapped[List[Optional[str]]] = _properties  # type: ignore

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    ACSUSR_0: Mapped[str] = mapped_column(Unicode(10, 'Latin1_General_BIN2'), default=text("''"))
    NEWPAS_0: Mapped[str] = mapped_column(Unicode(24, 'Latin1_General_BIN2'), default=text("''"))
    BPAADD_0: Mapped[str] = mapped_column(Unicode(5, 'Latin1_General_BIN2'), default=text("''"))
    BIDNUM_0: Mapped[str] = mapped_column(Unicode(30, 'Latin1_General_BIN2'), default=text("''"))
    RPCREP_0: Mapped[int] = mapped_column(SmallInteger, default=text('((0))'))
    USRPRT_0: Mapped[str] = mapped_column(Unicode(5, 'Latin1_General_BIN2'), default=text("''"))
    TIT_0: Mapped[str] = mapped_column(Unicode(250, 'Latin1_General_BIN2'), default=text("''"))
    ADDNAM_0: Mapped[str] = mapped_column(Unicode(250, 'Latin1_General_BIN2'), default=text("''"))
    PRFXTD_0: Mapped[str] = mapped_column(Unicode(5, 'Latin1_General_BIN2'), default=text("''"))
    ARCPRF_0: Mapped[str] = mapped_column(Unicode(10, 'Latin1_General_BIN2'), default=text("''"))
    FNC_0: Mapped[int] = mapped_column(TINYINT, default=text('((0))'))
    FLGPASPRV_0: Mapped[int] = mapped_column(TINYINT, default=text('((0))'))
    STA_0: Mapped[int] = mapped_column(TINYINT, default=text('((0))'))
    WITHOUTLDAP_0: Mapped[int] = mapped_column(TINYINT, default=text('((0))'))
    MSNSTR_0: Mapped[datetime.datetime] = mapped_column(DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'"))
    MSNEND_0: Mapped[datetime.datetime] = mapped_column(DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'"))
    MNA_0: Mapped[int] = mapped_column(TINYINT, default=text('((0))'))
    KILRAT_0: Mapped[decimal.Decimal] = mapped_column(Numeric(14, 3), default=text('((0))'))
    CUR_0: Mapped[str] = mapped_column(Unicode(3, 'Latin1_General_BIN2'), default=text("''"))
    FULTIM_0: Mapped[int] = mapped_column(TINYINT, default=text('((0))'))
    NBDAY_0: Mapped[int] = mapped_column(SmallInteger, default=text('((0))'))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='AUSDAY',
        property_name='ausday',
        count=7,
        column_type=TINYINT,
        python_type=int,
        default=text('((0))'),
    )

    ausdays: Mapped[List[Optional[int]]] = _properties  # type: ignore

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='ARVHOU',
        property_name='arrival_time',
        count=7,
        column_type=Unicode,
        column_args=(6, 'Latin1_General_BIN2'),
        python_type=str,
        default=text("''"),
    )

    arrival_times: Mapped[List[Optional[str]]] = _properties  # type: ignore

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='DPEHOU',
        property_name='departure_time',
        count=7,
        column_type=Unicode,
        column_args=(6, 'Latin1_General_BIN2'),
        python_type=str,
        default=text("''"),
    )

    departure_times: Mapped[List[Optional[str]]] = _properties  # type: ignore

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    ESCSTRDAT_0: Mapped[datetime.datetime] = mapped_column(DateTime, default=text(f"'{DEFAULT_LEGACY_DATETIME}'"))
    NBRESC_0: Mapped[int] = mapped_column(SmallInteger, default=text('((0))'))
    HDKREP_0: Mapped[int] = mapped_column(TINYINT, default=text('((0))'))
    AUZDSCDEM_0: Mapped[int] = mapped_column(TINYINT, default=text('((0))'))
    ACCCOD_0: Mapped[str] = mapped_column(Unicode(10, 'Latin1_General_BIN2'), default=text("''"))
    WRH_0: Mapped[str] = mapped_column(Unicode(5, 'Latin1_General_BIN2'), default=text("''"))

    def to_dict(self, include=None, exclude=None) -> dict:
        """
        Convert the Users object to a dictionary, excluding sensitive fields.
        :param include: Fields to include in the output dictionary.
        :param exclude: Fields to exclude from the output dictionary.
        :return: Dictionary representation of the Users object.
        """
        mapper = inspect(self.__class__)
        data = {}

        include = set(include) if include else None
        exclude = set(exclude) if exclude else set()

        for attr in mapper.attrs:
            key = attr.key

            # If include is specified, only include those keys
            if include and key not in include:
                continue

            # If exclude is specified, skip those keys
            if key in exclude:
                continue

            data[key] = getattr(self, key)

        return data
