import datetime

from sqlalchemy import DateTime, Index, PrimaryKeyConstraint, SmallInteger, Unicode
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base

from .generics_mixins import ArrayColumnMixin
from .mixins import AuditMixin, PrimaryKeyMixin


class Countries(Base, AuditMixin, PrimaryKeyMixin, ArrayColumnMixin):
    __tablename__ = 'TABCOUNTRY'
    __table_args__ = (
        PrimaryKeyConstraint('ROWID', name='TABCOUNTRY_ROWID'),
        Index('TABCOUNTRY_TCY0', 'CRY_0', unique=True),
        {'schema': 'TGN'},
    )

    country: Mapped[str] = mapped_column('CRY_0', Unicode(3, 'Latin1_General_BIN2'))
    CUR_0: Mapped[str] = mapped_column(Unicode(3, 'Latin1_General_BIN2'))
    EECCOD_0: Mapped[str] = mapped_column(Unicode(3, 'Latin1_General_BIN2'))
    CINSEE_0: Mapped[str] = mapped_column(Unicode(5, 'Latin1_General_BIN2'))
    ISO_0: Mapped[str] = mapped_column(Unicode(2, 'Latin1_General_BIN2'))
    ISOA3_0: Mapped[str] = mapped_column(Unicode(3, 'Latin1_General_BIN2'))
    ISONUM_0: Mapped[str] = mapped_column(Unicode(3, 'Latin1_General_BIN2'))
    LAN_0: Mapped[str] = mapped_column(Unicode(3, 'Latin1_General_BIN2'))
    EECFLG_0: Mapped[int] = mapped_column(TINYINT)
    EECDAT_0: Mapped[datetime.datetime] = mapped_column(DateTime)
    EECDATOUT_0: Mapped[datetime.datetime] = mapped_column(DateTime)
    CTLPRG_0: Mapped[str] = mapped_column(Unicode(30, 'Latin1_General_BIN2'))
    NAFFMT_0: Mapped[str] = mapped_column(Unicode(30, 'Latin1_General_BIN2'))
    TELFMT_0: Mapped[str] = mapped_column(Unicode(30, 'Latin1_General_BIN2'))
    POSCODFMT_0: Mapped[str] = mapped_column(Unicode(30, 'Latin1_General_BIN2'))
    POSCODCRY_0: Mapped[str] = mapped_column(Unicode(30, 'Latin1_General_BIN2'))
    CTYCODFMT_0: Mapped[str] = mapped_column(Unicode(30, 'Latin1_General_BIN2'))
    CTYUPP_0: Mapped[int] = mapped_column(TINYINT)
    CTYNUMFMT_0: Mapped[str] = mapped_column(Unicode(30, 'Latin1_General_BIN2'))
    ADRCODFMT_0: Mapped[str] = mapped_column(Unicode(30, 'Latin1_General_BIN2'))
    MINZIP_0: Mapped[int] = mapped_column(SmallInteger)
    ADRNAM_0: Mapped[str] = mapped_column(Unicode(20, 'Latin1_General_BIN2'))
    ADRNAM_1: Mapped[str] = mapped_column(Unicode(20, 'Latin1_General_BIN2'))
    ADRNAM_2: Mapped[str] = mapped_column(Unicode(20, 'Latin1_General_BIN2'))
    BIDFMT_0: Mapped[str] = mapped_column(Unicode(30, 'Latin1_General_BIN2'))
    PABFMT_0: Mapped[str] = mapped_column(Unicode(30, 'Latin1_General_BIN2'))
    BIDCRY_0: Mapped[str] = mapped_column(Unicode(30, 'Latin1_General_BIN2'))
    CRNFMT_0: Mapped[str] = mapped_column(Unicode(30, 'Latin1_General_BIN2'))
    CRTFMT_0: Mapped[str] = mapped_column(Unicode(30, 'Latin1_General_BIN2'))
    NIDFMT_0: Mapped[str] = mapped_column(Unicode(30, 'Latin1_General_BIN2'))
    EECFMT_0: Mapped[str] = mapped_column(Unicode(30, 'Latin1_General_BIN2'))
    CRNFMTFLG_0: Mapped[int] = mapped_column(TINYINT)
    CRTFMTFLG_0: Mapped[int] = mapped_column(TINYINT)
    NIDFMTFLG_0: Mapped[int] = mapped_column(TINYINT)
    EECFMTFLG_0: Mapped[int] = mapped_column(TINYINT)
    NAFFMTFLG_0: Mapped[int] = mapped_column(TINYINT)
    SUBDIVFMT_0: Mapped[str] = mapped_column(Unicode(30, 'Latin1_General_BIN2'))
    CRYVATNUM_0: Mapped[str] = mapped_column(Unicode(3, 'Latin1_General_BIN2'))
    CONTINENT_0: Mapped[str] = mapped_column(Unicode(20, 'Latin1_General_BIN2'))
    ETAT_0: Mapped[int] = mapped_column(TINYINT)
    ETATFLG_0: Mapped[int] = mapped_column(TINYINT)
    ETATFLG2_0: Mapped[int] = mapped_column(TINYINT)
    ETATFMT_0: Mapped[str] = mapped_column(Unicode(30, 'Latin1_General_BIN2'))
    ETATFMT2_0: Mapped[str] = mapped_column(Unicode(30, 'Latin1_General_BIN2'))
    ETATCTL_0: Mapped[int] = mapped_column(TINYINT)
    SOCNUMFLG1_0: Mapped[int] = mapped_column(SmallInteger)
    POSCODCTL_0: Mapped[int] = mapped_column(TINYINT)
    BIDCTL_0: Mapped[int] = mapped_column(TINYINT)
    BANLNG_0: Mapped[int] = mapped_column(SmallInteger)
    FLIBAN_0: Mapped[int] = mapped_column(TINYINT)
    POSOBL_0: Mapped[int] = mapped_column(TINYINT)
    SOCNUMFMT_0: Mapped[str] = mapped_column(Unicode(1, 'Latin1_General_BIN2'))
    CRNOBL_0: Mapped[int] = mapped_column(TINYINT)
    CRTOBL_0: Mapped[int] = mapped_column(TINYINT)
    TELTCY_0: Mapped[str] = mapped_column(Unicode(10, 'Latin1_General_BIN2'))
    TELREG_0: Mapped[str] = mapped_column(Unicode(10, 'Latin1_General_BIN2'))
    FLGSEPA_0: Mapped[int] = mapped_column(TINYINT)
    SOCNUMFLG2_0: Mapped[int] = mapped_column(SmallInteger)
    BIDCLS_0: Mapped[str] = mapped_column(Unicode(12, 'Latin1_General_BIN2'))
    SOCNUMFMT2_0: Mapped[str] = mapped_column(Unicode(1, 'Latin1_General_BIN2'))
    FLGDUE_0: Mapped[int] = mapped_column(TINYINT)
    GSPFLG_0: Mapped[int] = mapped_column(TINYINT)
    EORIFLG_0: Mapped[int] = mapped_column(TINYINT)
    ZBCTFFLG_0: Mapped[int] = mapped_column(TINYINT)
