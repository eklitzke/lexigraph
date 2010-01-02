import datetime
from tempest.view.api._common import *

class CreatePoint(ApiRequestHandler):

    @encode_json
    def post(self):

        # get the series obj
        series = int(self.request.get('series'))
        series = SeriesSchema.get_by_id(series)

        value = float(self.request.get('value'))
        timestamp = self.request.get('timestamp')
        if not timestamp:
            timestamp = datetime.datetime.now()
        else:
            timestamp = datetime.datetime.fromtimestamp(int(timestamp))
        point = DataPoint(series=series, value=value, timestamp=timestamp)
        point.put()
        return {'status': StatusCodes.OK, 'id': point.key().id()}

__all__ = ['CreatePoint']
