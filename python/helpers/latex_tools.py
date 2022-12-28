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
    }.items():
        s = s.replace(k, v)
    return s
