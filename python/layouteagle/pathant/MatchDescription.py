import itertools
from pprint import pprint



def match(s1:str , s2: str, delimiter='.'):
    parts1 = [s1[::-1][:i][::-1] for i, c in enumerate(s1[::-1])  if c == delimiter]
    parts2 = [s2[:i] for i, c in enumerate(s2+'.') if c == delimiter]
    same_elements = [p1 for p1, p2 in
                     itertools.product(parts1, parts2) if p1==p2]
    return bool(same_elements)

def list_or_value(arg):
    if isinstance(arg, (list, set, tuple)):
        yield from arg
    else:
        yield arg

def list_or_values(*args):
    if args:
        rest = tuple(list_or_values(*args[1:]))
        for arg in list_or_value(args[0]):
            if rest:
                for r in rest:
                    if isinstance(r, (list, set, tuple)):
                        yield (arg, *r)
                    else:
                        yield (arg, r)
            else:
                yield arg




if __name__ == "__main__":
    def task(s1, s2, moral):
        matches = match(s1,s2)
        return (f"{'ok' if matches == moral else 'BAD!'} {s1} and {s2} { 'matches' if matches else 'not'}")

    tasks = [('graph.dict', 'dings.graph', False),
            ('dings.graph', 'graph', True),
             ('topics.dict', 'dict', True)]
    results = [task(*args) for args in tasks]
    print ("\n".join(results))

    pprint (list(list_or_values('1', ('abc', 'cde'), '2', ['tt', 'ee'])))

