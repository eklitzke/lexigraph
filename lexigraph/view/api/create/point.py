import datetime
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
            dataset = self.get_dataset(dataset)
            if dataset is None:
                return self.make_error(StatusCodes.INVALID_FIELD, invalid='dataset')
        except PermissionsError:
            raise

        value = float(self.request.get('value'))
        timestamp = self.request.get('timestamp')
        if not timestamp:
            timestamp = datetime.datetime.now()
        else:
            timestamp = datetime.datetime.fromtimestamp(int(timestamp))

        dataset.add_points(value, timestamp)
        return self.add_status({}, StatusCodes.OK)

add_route(CreatePoint, '/api/new/datapoint')
