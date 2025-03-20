from itertools import groupby


def associateby(iterable, key_selector):
    return {k: next(v) for k, v in groupby(iterable, key_selector)}
