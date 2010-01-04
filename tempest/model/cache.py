from tempest.model.db import *
from tempest.cache import CacheDict

class DataSetCache(CacheDict):
    namespace = 'data_set'

    @classmethod
    def lookup(cls, name):
        cache_obj = cls()
        ds = cache_obj[name]
        if ds is not None:
            return ds
        val, = DataSet.all().filter('name =', name).fetch(1)
        cache_obj[name] = val
        return val
