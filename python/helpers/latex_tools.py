import logging

import regex


def latex_replace(s):
    for k, v in {
        "\\N{RIGHT SINGLE QUOTATION MARK}": "'",
        "\\N{LEFT SINGLE QUOTATION MARK}": "'",
        "\\N{BULLET}": "*",
        "\\N{RIGHT DOUBLE QUOTATION MARK}": '"',
        "\\N{LEFT DOUBLE QUOTATION MARK}": '"',
        "\\N{HORIZONTAL ELLIPSIS}": "",
        "\\N{LATIN}": "",
        "\\N{DEGREE SIGN}": "°",
        "\\N{LATIN SMALL LIGATURE FL}": "fl",
        "\\N{LATIN SMALL LIGATURE FF}": "ff",
        "\\N{LATIN SMALL LIGATURE FI}": "fi",
        "\\N{LATIN SMALL LETTER E WITH ACUTE}": "é",
        "\\N{BLACK SMALL SQUARE}": "*",
        "\\N{EN DASH}": "-",
        "\\N{EM DASH}": "-",
        "\\N{NO-BREAK SPACE}": " ",
        "\\N{COPYRIGHT SIGN}": "©",
        "\\N{LATIN SMALL LETTER O WITH DIAERESIS}": "o",
        "\\N{LATIN SMALL LETTER U WITH DIAERESIS}": "u",
        "\\N{LATIN SMALL LETTER A WITH DIAERESIS}": "a",
        "\\N{LATIN SMALL LETTER E WITH DIAERESIS}": "e",
        "\\N{LATIN SMALL LETTER I WITH DIAERESIS}": "i",
        "\\N{LATIN SMALL LETTER O WITH MACRON}": 'o',
        "\\N{THIN SPACE}": " "

    }.items():
        s = s.replace(k, v)
    for m in regex.findall(r"\\N\{[\w\s\d]+\}", s):
        print(m)

    s2 = regex.sub(r"\\N\{[\w\s\d]+\}", s, "")
    if not s2:
        logging.info("regex replaced whole string")
        return s
    return s2
