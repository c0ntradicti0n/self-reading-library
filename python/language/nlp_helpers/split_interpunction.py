import regex as re


def flatten(t):
    return [item for sublist in t for item in sublist]


def split_punctuation(s, punctuations):
    """simple tokenizer...

    >>> split_punctuation("sentence, bla... end. go further. and here! also at the end?", "!?.:,;")
    ['sentence', ',', 'bla', '...', 'end', '.', 'go', 'further', '.', 'and', 'here', '!', 'also', 'at', 'the', 'end', '?']

    """
    if len(punctuations) == 0:
        return s.split()
    else:
        separator, *rest = punctuations

        things = []
        for word in re.split(rf"(?<=[a-zA-Z][a-zA-Z])(?=\{separator})(?:/d)*", s):
            things.append(split_punctuation(word, rest))
        return flatten(things)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
