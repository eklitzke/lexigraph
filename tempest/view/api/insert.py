from tempest.view.api._common import *

class Insert(ApiRequestHandler):

    def get(self):
        return 404

    @encode_json
    def post(self):
        series = self.fetch_data_set()
        return series

__all__ = ['Insert']
