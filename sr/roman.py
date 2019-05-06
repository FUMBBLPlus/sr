# Based on Mark Pilgrim - Dive Into Python 3

import re


ROMAN_NUMS = ("I", "V", "X", "L", "C", "D", "M")

ROMAN_NUM_MAP = (("M", 1000), ("CM", 900), ("D",  500),
    ("CD", 400), ("C",  100), ("XC",  90), ("L",   50),
    ("XL",  40), ("X",   10), ("IX",   9), ("V",    5),
    ("IV",   4), ("I",    1))

ROMAN_REPAT = re.compile("""
    ^                   # start of string
    M{0,3}              # thousands, 1-3 M
    (CM|CD|D?C{0,3})    # hundreds - 900 (CM), 400 (CD),
                        #     0-300 (0-3 C), or
                        #     500-800 (D + 1-3 C)
    (XC|XL|L?X{0,3})    # tens - 90 (XC), 40 (XL),
                        #     0-30 (0-3 X), or
                        #     50-80 (L + 0-3 X)
    (IX|IV|V?I{0,3})    # ones - 9 (IX), 4 (IV), 0-3 (0-3 I),
                        #     or 5-8 (V + 0-3 I)
    $                   # end of string
    """, re.VERBOSE)


def to_roman(val):
    """
    Converts an integer to a roman numeral.

    Example:
    >>> to_roman("2013")
    'MMXIII'
    """
    integer, result = int(val), ""

    if not (0 < integer < 4000):
        raise ValueError("Value must be between 0 and 4000")

    for roman_num, roman_integer in ROMAN_NUM_MAP:
        while integer >= roman_integer:
            result += roman_num
            integer -= roman_integer

    return result


def from_roman(s, accept_lower=False):
    """
    Converts a roman numeral to an integer.

    Examples:
    >>> from_roman("MMXIII")
    2013
    >>> from_roman("mmxiii", True)
    2013
    """
    if not s:
        raise ValueError("Empty string")

    result, i = 0, 0
    if accept_lower:
        s = s.upper()

    if not ROMAN_REPAT.search(s):
        raise ValueError("Invalid roman numeral")

    for roman_num, roman_integer in ROMAN_NUM_MAP:
        while s[i:i+len(roman_num)] == roman_num:
            result += roman_integer
            i += len(roman_num)

    return result
