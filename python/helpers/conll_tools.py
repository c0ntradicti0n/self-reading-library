from language.transformer.core.bio_annotation import conll_line


def conll2annotation(content):
    cols = list(
        zip(
            *[
                m.groups()
                for i, line in enumerate(content.split("\n"))
                if line and (m := conll_line.match(line.replace("\t", "  ")))
            ]
        )
    )
    result = {"annotation": list(zip(cols[0], cols[-1])), "pos": cols[1]}
    return result


def conll_file2annotation(pickle_path):
    with open(pickle_path, errors="ignore") as f:
        content = f.read()
    result = conll2annotation(content)
    return result
