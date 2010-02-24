import re

from lexigraph.view import add_route
from lexigraph.handler import SessionHandler
class GraphQuery(SessionHandler):

    requires_login = True

    def initialize(self, request, response):
        super(GraphQuery, self).initialize(request, response)
        response.headers['Content-Type'] = 'application/json'

    def get(self):
        q = self.request.get('q') or ''
        tags = set(x.strip() for x in q.split(',') if x.strip())
        datasets = TagQueryCache().select_by_tags(self.account, self.user, tags)
        self.render_json({'status': True, 'datasets': datasets})

add_route(GraphQuery, '/graph/query')
