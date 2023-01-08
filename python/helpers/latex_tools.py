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
        "\\N{LATIN SMALL LIGATURE FF}": "ff",
        "\\N{LATIN SMALL LIGATURE FI}": "fi",
        "\\N{LATIN SMALL LETTER E WITH ACUTE}": "é",
        "\\N{BLACK SMALL SQUARE}": "*",
        "\\N{EN DASH}": "-",
        "\\N{NO-BREAK SPACE}": " ",
        "\\N{COPYRIGHT SIGN}": "©",
    }.items():
        s = s.replace(k, v)
    for m in regex.findall(r"\\N\{[\w\s\d]+\}", s):
        print(m)

    s = regex.sub(r"\\N\{[\w\s\d]+\}", s, "")
    return s
