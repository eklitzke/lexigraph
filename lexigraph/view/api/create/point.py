import datetime
from lexigraph.view.api._common import *

class CreatePoint(ApiRequestHandler):

    @encode_json
    def post(self):

        dataset = self.get_dataset(self.form_required('name'))

        dataset = self.request.get('dataset')
        if not dataset:
            return self.make_error(StatusCodes.MISSING_PARAM, missing='dataset')
        try:
            dataset = self.get_dataset(dataset)
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

__all__ = ['CreatePoint']
