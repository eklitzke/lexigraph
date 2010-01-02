from google.appengine.ext import db

class AggregateType(object):
    MIN = 1
    MAX = 2
    SUM = 3
    AVG = 4
    OLD = 5
    NEW = 6

    @classmethod
    def from_string(cls, s):
        return getattr(cls, s.upper())

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

class TempestModel(db.Model):

    def to_python(self):
        d = {}
        for k in self.properties().iterkeys():
            d[k] = getattr(self, k)
        return to_python(d)

class DataSet(TempestModel):
    name = db.StringProperty(required=True) # unique
    aggregate = db.IntegerProperty(required=True)
    attributes = db.StringListProperty() # optional

class SeriesSchema(TempestModel):
    data_set = db.ReferenceProperty(DataSet, required=True)
    interval = db.IntegerProperty(required=True)
    max_age = db.IntegerProperty()

class DataSeries(TempestModel):
    series = db.ReferenceProperty(SeriesSchema, required=True)
    value = db.FloatProperty(required=True)
    timestamp = db.DateTimeProperty(required=True, auto_now_add=True)
