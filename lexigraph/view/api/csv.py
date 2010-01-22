import time
import math
from lexigraph.view import add_route
from lexigraph.view.api._common import *

from lexigraph import model
from lexigraph.model.query import *

LIMIT = 1000

class CSV(ApiRequestHandler):

    def initialize(self, request, response):
        super(CSV, self).initialize(request, response)
        response.headers['Content-Type'] = 'text/csv; charset=us-ascii'

    def process_form(self):
        super(CSV, self).process_form()
        dataset = self.request.get('dataset')
        if not dataset:
            return self.make_error(StatusCodes.MISSING_FIELD, field='dataset')

        try:
            self.dataset = self.get_dataset(dataset)
        except PermissionsError:
            return self.make_error(StatusCodes.PERMISSIONS_ERROR, field='dataset')

        # max points allowed in the CSV
        self.max_points = self.request.get('max_points', 750)

        # hint on how many points to try to have in the CSV
        self.points = self.request.get('points', 400)

        # timespan, in seconds (default: four hours)
        self.span = self.request.get('span', 4 * 3600)

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

    def get_worker(self):

        # Figure out the best series to use. We're trying to achieve a chart
        # with self.points points in it, and strictly at most self.max_points
        # points. It's better to have too many points than it is to have too
        # few.

        self.response.out.write('Timestamp,Value\n')

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
        for c in fetch_all(model.DataSeries.all().filter('dataset =', self.dataset)):
            points_required, score = score_candidate(c)
            self.log.debug('considering %s; points_required = %s, score = %s' % (c, points_required, score))
            if score >= 0:
                candidates.append((c, score, points_required))

        if not candidates:
            self.log.info('No candidates could fulfill CSV request for %s' % (self.request.uri,))
            return

        # pick the best candidate
        series, score, points_required = min(candidates, key=lambda (a, b, c): b)
        self.log.info('Chose series %s, score = %s, points_required = %d' % (series, score, points_required))
        for point in self.fetch_ordered_points(span=self.span, limit=points_required, python_order=True):
            self.response.out.write('%s,%s\n' % (point.timestamp.strftime('%Y/%m/%d %H:%M:%S'), point.value))

add_route(CSV, '/api/csv')
