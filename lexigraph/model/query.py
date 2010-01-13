class TooManyResults(ValueError):
    pass

def maybe_one(query):
    results = query.fetch(limit=1)
    if len(results) == 0:
        return None
    elif len(results) == 1:
        return results[0]
    else:
        raise TooManyResults('Unexpectedly got results: %r' % (results,))
