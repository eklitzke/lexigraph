from lexigraph.view import add_route
from lexigraph.handler import SessionHandler
from lexigraph import model
from lexigraph.model.query import *

class GraphQuery(SessionHandler):

    requires_login = True

    def initialize(self, request, response):
        super(GraphQuery, self).initialize(request, response)
        response.headers['Content-Type'] = 'application/json'

    def get(self):
        q = self.request.get('q') or ''
        tags = set(x.strip() for x in q.split(','))
        query = model.DataSet.all()
        for tag in (t for t in tags if t):
            query = query.filter('tags =', tag)
        datasets = fetch_all(query)

        # Filter out datasets to include only ones the user can read. Collect
        # only the names of the datasets.
        datasets = [d.name for d in datasets if d.is_allowed(self.user, read=True)]
        self.log.info('selected datasets = %s' % (datasets,))

        self.render_json({'status': True, 'datasets': datasets})

add_route(GraphQuery, '/graph/query')
