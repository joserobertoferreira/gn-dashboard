"""Enumerações e constantes do Sage X3 (menus locais e outros códigos)."""

from enum import IntEnum


class Chapter1(IntEnum):
    """Menu local 1 do Sage X3: Não/Sim."""

    NO = 1
    YES = 2


class Chapter645(IntEnum):
    """Menu local 645 do Sage X3: tipo de fatura."""

    INVOICE = 1
    CREDIT_NOTE = 2
    DEBIT_NOTE = 3
    CREDIT_MEMO = 4
    PROFORMA = 5


class TaxLevel(IntEnum):
    """Taxas de IVA (%)."""

    TDN = 23
    TDI = 13
    TDR = 6


#: Código de pagamento múltiplo.
MULTI_PAYMENTS = 9
