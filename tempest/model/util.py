def to_python(obj):
    """Introspect an object, converting it to builtin objects all the way down.
    """
    if obj is None:
        return obj
    obj_t = type(obj)
    if obj_t in (int, long, float, str, unicode):
        return obj
    elif obj_t in (set, frozenset, list, tuple):
        return obj.__class__(to_python(v) for v in obj)
    elif obj_t is dict:
        return dict((to_python(k), to_python(v)) for k, v in obj.iteritems())
    elif hasattr(obj, 'to_python'):
        return to_python(obj.to_python())
    else:
        raise TypeError('Error converting %r to python, class = %s' % (obj, obj.__class__))
