import regex as re


def flatten(t):
    return [item for sublist in t for item in sublist]


PUNCTUATIONS = ".,:!?;()[]{}"


def split_punctuation(s, matches=False, REST=PUNCTUATIONS):
    """simplest tokenizer...

    >>> split_punctuation("sentence, bla... end. go further. and here! also at the end?")
    ['sentence', ',', 'bla', '...', 'end', '.', 'go', 'further', '.', 'and', 'here', '!', 'also', 'at', 'the', 'end', '?']

    """
    if len(REST) == 0:
        if matches:
            return list([word for word in re.split(r"(\s+)", s)])
        return s.split()
    else:
        separator, *rest = REST

        things = []
        for word in re.split(
            rf"(?<=[a-zA-Z][a-zA-Z])(?=\{separator})(?:/d)*", s, matches
        ):
            things.append(split_punctuation(word, REST=rest, matches=matches))
        return flatten(things)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
