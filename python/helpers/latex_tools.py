def latex_replace(s):
    for k, v in {r"\N{RIGHT SINGLE QUOTATION MARK}": "'"}.items(
    ):
        s = s.replace(k, v)
    return s