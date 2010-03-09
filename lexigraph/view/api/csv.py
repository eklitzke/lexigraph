import time
import math
from collections import defaultdict

from lexigraph import config
from lexigraph.view import add_route
from lexigraph.view.api._common import *
from lexigraph.handler import SessionHandler

from lexigraph import model

class CSV(ApiRequestHandler, SessionHandler):

    def initialize(self, request, response):
        super(CSV, self).initialize(request, response)
        response.headers['Content-Type'] = 'text/csv; charset=us-ascii'

    def process_form(self):
        super(CSV, self).process_form()

        datasets = self.request.get_all('dataset')
        if not datasets:
            return self.make_error(StatusCodes.MISSING_FIELD, field='dataset')

        self.datasets = []
        try:
            for dataset in datasets:
                ds = model.DataSet.from_encoded(dataset, user=self.user, api_key=self.key)
                if not ds:
                    raise KeyError("No such dataset %r" % (dataset,))
                self.datasets.append(ds)
        # FIXME: handle unknown datasets
        except PermissionsError:
            return self.make_error(StatusCodes.PERMISSIONS_ERROR, field='dataset')

        # max points allowed in the CSV
        self.max_points = self.request.get('max_points', 750)

        # hint on how many points to try to have in the CSV
        self.points = self.request.get('points', 400)

        # timespan for the graph
        self.span = self.request.get('span', config.default_timespan)

    def fetch_ordered_points(self, series, span=None, limit=None, python_order=False):
        """Fetch the points. This takes a bunch of different permutations of
        arguments, for easy of experimenting with what is most efficient. Here's
        what they mean:

        span: if not None, add a clause to the query like "timestamp >= now() -
              span"

        limit: the limit of points to fetch (well be self.max_points if not
              specified)
        
        python_order: if True, run sorted() in the Python code. if False, do an
              order by query.
        """
        if limit is None:
            limit = self.max_points
        if python_order:
            assert span
        query = DataPoint.all().filter('series =', series)
        if span is not None:
            query = query.filter('timestamp >=', datetime.datetime.now() - datetime.timedelta(seconds=span))
        if python_order:
            return sorted(query.fetch(limit), key=lambda x: x.timestamp)
        else:
            return reversed(query.order('-timestamp').fetch(limit))

    def get_points_for_dataset(self, dataset):

        # Figure out the best series to use. We're trying to achieve a chart
        # with self.points points in it, and strictly at most self.max_points
        # points. It's better to have too many points than it is to have too
        # few.

        def score_candidate(candidate):
            """Score a candidate DataSeries. This returns the tuple
            (points_required, score) for a candidate.

            XXX: this assumes that the series is "full" and has enough points.
            """
            # filter out candidates whose max_age is too small
            if candidate.max_age is not None and candidate.max_age < self.span:
                self.log.debug('max age is too small')
                return 0, -1

            points_required = int(math.ceil(self.span / candidate.interval))

            if points_required > self.max_points:
                self.log.debug('takes too many points: %d' % (points_required,))
                return 0, -1

            points_diff = points_required - self.points

            # too many points will be required
            if points_diff >= 0:
                return points_required, 0.5 * points_diff

            # too few points required
            return points_required, float(-points_diff)

        # candidates must have a positive score
        candidates = []
        for c in model.DataSeries.all().filter('dataset =', dataset):
            points_required, score = score_candidate(c)
            self.log.debug('considering %s; points_required = %s, score = %s' % (c, points_required, score))
            if score >= 0:
                candidates.append((c, score, points_required))

        if not candidates:
            self.log.info('No candidates could fulfill CSV request for %s' % (self.request.uri,))
            return

        # pick the best candidate
        series, score, points_required = min(candidates, key=lambda (a, b, c): b)
        self.log.info('Chose series %s, score = %s, points_required = %d (for dataset %s)' % (series, score, points_required, dataset))
        return list(self.fetch_ordered_points(series, span=self.span, limit=points_required, python_order=True))

    def get_worker(self):

        # simple and fast code if only one dataset
        if len(self.datasets) == 1:
            dataset = self.datasets[0]
            self.response.out.write('Timestamp,%s\n' % (dataset.name,))
            points = self.get_points_for_dataset(dataset)
            for p in points:
                self.response.out.write('%s,%s\n' % (p.timestamp.strftime('%s'), p.value))
        else:
            header = ['Timestamp'] + [ds.name for ds in self.datasets]
            self.response.out.write(','.join(header) + '\n')
            points = []
            for ds in self.datasets:
                points.append(self.get_points_for_dataset(ds))

            times = defaultdict(dict)
            dataset_names = [ds.name for ds in self.datasets]
            for name, point_list in zip(dataset_names, points):
                for p in point_list:
                    time = config.graph_resolution * (int(p.timestamp.strftime('%s')) / config.graph_resolution)
                    times[time][name] = p.value

            for t in sorted(times.keys()):
                vals = times[t]
                self.log.info('vals = %s' % (vals,))
                output = [t]
                for name in dataset_names:
                    output.append(vals.get(name, ''))
                self.response.out.write(','.join(str(x) for x in output) + '\n')

add_route(CSV, '/api/csv')
