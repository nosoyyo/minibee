from functools import reduce


def sumChars(_iterable) -> str:
    '''
    return the summation of list/set elements and many other stuff.
    '''
    _iterable = [str(i) for i in _iterable]
    chars = [c for c in _iterable if c.isalnum()]
    if not chars:
        chars = [c for i in _iterable for c in i if c.isalnum()]
    return reduce(lambda x, y: x+y, chars)
