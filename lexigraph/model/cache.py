from lexigraph.model.db import *
from lexigraph.cache import CacheDict

class RowCache(CacheDict):

    fields = None
    model = None

    @classmethod
    def lookup(cls, *fields):
        cache_obj = cls()
        ds = cache_obj[fields]
        if ds is not None:
            return ds
        query = cls.model.all()
        for field_name, field_val in zip(cls.fields, fields):
            query = query.filter(field_name + ' =', field_val)
        val, = query.fetch(1)
        cache_obj[fields] = val
        return val

class RowIdCache(RowCache):

    def normalize_key(self, k):
        return int(k[0])

class DataSetCache(RowCache):
    namespace = 'dataset_name'
    fields = ['name']
    model = DataSet

class SeriesCache(RowIdCache):
    namespace = 'series_id'
    fields = ['id']
    model = SeriesSchema

class SeriesNamedCache(CacheDict):
    """Keys by (dataset name, interval)"""
    namespace = 'series_cache'

    def normalize_key(self, val):
        name, ival = val
        return str(name), int(ival)

    @classmethod
    def lookup(cls, dataset_name, interval):
        cache_obj = cls()
        series = cache_obj[(dataset_name, interval)]
        if series is not None:
            return series

        ds = DataSetCache.lookup(dataset_name)
        val, = SeriesSchema.all().filter('data_set =', ds).filter('interval =', interval).fetch(1)
        cache_obj[(dataset_name, interval)] = val
        return val
