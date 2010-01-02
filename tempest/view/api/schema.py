from tempest.view.api._common import *
from tempest.model import *
from collections import defaultdict

class Schema(ApiRequestHandler):

    @encode_json
    def get(self):
        groups = defaultdict(list)
        for series in SeriesSchema.all().fetch(limit=100):
            groups[series.data_set].append(series)
        return groups.items()

__all__ = ['Schema']
