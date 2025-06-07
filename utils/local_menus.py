from enum import IntEnum


class Chapter1(IntEnum):
    """Chapter 1: YES or NO"""

    NO = 1
    YES = 2


class Chapter645(IntEnum):
    """Chapter 645: Invoice Type"""

    INVOICE = 1
    CREDIT_NOTE = 2
    DEBIT_NOTE = 3
    CREDIT_MEMO = 4
    PROFORMA = 5
