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
        self.dataset = maybe_one(model.DataSet.all().filter('name =', dataset).filter('account =', self.current_account))
        if self.dataset is None:
            return self.make_error(StatusCodes.INVALID_FIELD, field='dataset')

        # validate the permissions for the dataset
        if not self.dataset.is_allowed(api_key=self.key, read=True):
            return self.make_error(StatusCodes.PERMISSIONS_ERROR, field='dataset')

        # max points allowed in the CSV
        self.max_points = self.request.get('max_points', 750)

        # hint on how many points to try to have in the CSV
        self.points = self.request.get('points', 400)

        # timespan, in seconds (default: four hours)
        self.span = self.request.get('span', 4 * 3600)

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
        points = DataPoint.all().filter('series =', series).order('-timestamp').fetch(points_required)
        for point in reversed(points):
            self.response.out.write('%s,%s\n' % (point.timestamp.strftime('%Y/%m/%d %H:%M:%S'), point.value))

add_route(CSV, '/api/csv')
