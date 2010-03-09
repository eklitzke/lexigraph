import datetime
from lexigraph import model
from lexigraph.view import add_route
from lexigraph.handler import RequestHandler
from lexigraph.view.api._common import *

class CreatePoint(ApiRequestHandler):

    @encode_json
    def post(self):
        dataset = self.form_required('dataset')
        if not dataset:
            return self.make_error(StatusCodes.MISSING_FIELD, missing='dataset')
        try:
            dataset = model.DataSet.from_encoded(dataset, api_key=self.key)
            if dataset is None:
                return self.make_error(StatusCodes.INVALID_FIELD, invalid='dataset')
        except PermissionsError:
            raise
        try:
            value = float(self.request.get('value'))
        except ValueError:
            raise # FIXME
        timestamp = self.request.get('timestamp')
        if not timestamp:
            timestamp = datetime.datetime.now()
        else:
            timestamp = datetime.datetime.fromtimestamp(int(timestamp))

        dataset.add_points(value, timestamp)
        return self.add_status({}, StatusCodes.OK)

add_route(CreatePoint, '/api/new/datapoint')
