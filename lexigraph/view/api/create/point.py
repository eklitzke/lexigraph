import datetime
from lexigraph import model
from lexigraph.view import add_route
from lexigraph.handler import RequestHandler
from lexigraph.view.api._common import *

class CreatePoint(ApiRequestHandler):

    def get_datasets(self, datasets):
        result = []
        for ds in datasets:
            dataset = model.DataSet.from_encoded(ds, api_key=self.key, write=True)
            assert dataset is not None
            result.append(dataset)
        return result

    def get_timestamps(self, timestamps):
        ts = []
        now = datetime.datetime.now()
        for t in timestamps:
            t = int(t)
            if t:
                t = datetime.datetime.fromtimestamp(t)
            else:
                t = now
            ts.append(t)
        return ts

    @encode_json
    def post(self):
        """Add one or more DataPoints. To add multiple points from a single
        request, you simply repeat the dataset/value/timestamp form variables.
        """
        datasets = self.request.get_all('dataset')
        values = self.request.get_all('value')
        timestamps = self.request.get_all('timestamp')

        assert datasets

        if not timestamps:
            timestamps = [0 for x in xrange(len(datasets))]
        assert len(datasets) == len(values)
        assert len(datasets) == len(timestamps)

        values = [float(v) for v in values]
        datasets = self.get_datasets(datasets)
        timestamps = self.get_timestamps(timestamps)

        for ds, v, t in zip(datasets, values, timestamps):
            ds.add_points(v, t)
        return self.add_status({}, StatusCodes.OK)

add_route(CreatePoint, '/api/new/datapoint')
