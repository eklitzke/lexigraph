from lexigraph.view import add_route
from lexigraph.handler import SessionHandler
from lexigraph import model
from lexigraph.cache import CacheDict
from lexigraph.model.query import *

class TagQueryCache(CacheDict):

    def normalize_key(self, (account, user, tag_list)):
        return (account.key().id(), user.user_id(), sorted(tag_list))

    def select_by_tags(self, account, user, tag_list):
        """Return datasets containing all tags in the list."""
        val = self[(account, user, tag_list)]
        if val is None:
            q = model.DataSet.all().filter('account =', account)
            for tag in tag_list:
                q = q.filter('tags =', tag)
            val = [ds.name for ds in fetch_all(q) if ds.is_allowed(user, read=True)]
            self[(account, user, tag_list)] = val
        return val

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
