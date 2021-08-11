def gen_primes(limit=999999):  # derived from
    # Code by David Eppstein, UC Irvine, 28 Feb 2002
    D = {}  # http://code.activestate.com/recipes/117119/
    q = 2

    while q <= limit:
        if q not in D:
            yield q
            D[q * q] = [q]
        else:
            for p in D[q]:
                D.setdefault(p + q, []).append(p)
            del D[q]
        q += 1


if __name__ == "__main__":
    print(list(gen_primes(200)))