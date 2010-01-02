from tempest.view.api._common import *
from tempest.model import *
from collections import defaultdict

LIMIT = 100

class Schema(ApiRequestHandler):

    @encode_json
    def get(self):
        groups = defaultdict(list)
        for series in SeriesSchema.all().fetch(limit=LIMIT):
            groups[series.data_set].append(series)
        groups = dict(groups.iteritems())
        empty_sets = DataSet.all().fetch(limit=LIMIT)
        for es in (e for e in empty_sets if e not in groups):
            groups[es] = []
        
        return to_python(groups.items())

__all__ = ['Schema']
