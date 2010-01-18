class TooManyResults(ValueError):
    pass

def _pick_one(results):
    if len(results) == 0:
        return None
    elif len(results) == 1:
        return results[0]
    else:
        raise TooManyResults('results = %r '% (results,))

def maybe_one(query):
    return _pick_one(query.fetch(limit=1))

def fetch_all(query):
    return query.fetch(1000)