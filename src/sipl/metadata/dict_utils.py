import collections


def flatten(nested, parent='', sep='/'):
    flattened = {}
    for key, value in nested.iteritems():
        flat_key = parent + sep + key if parent else key
        if isinstance(value, collections.MutableMapping):
            flattened.update(flatten(value, flat_key, sep))
        else:
            flattened[flat_key] = value
    return flattened


def nest(flattened, sep='/'):
    nested = {}
    for key, value in flattened.iteritems():
        head, _, tail = key.partition(sep)
        if not tail:
            nested[head] = value
        else:
            nested[head] = nest({tail: value}, sep)
    return nested
