import time
import math
from collections import defaultdict

from lexigraph import config
from lexigraph.view import add_route
from lexigraph.view.api._common import *
from lexigraph.handler import SessionHandler

from lexigraph import model

class Description(ApiRequestHandler, SessionHandler):
    """Returns a JSON description of available entities in the API."""

    def get_worker(self):

        datasets = []
        for ds in model.DataSet.all().filter('account =', self.account):
            if ds.is_allowed(self.user, self.account, read=True):
                datasets.append({'key': ds.encode(),
                                 'name': ds.name,
                                 'aggregate': ds.aggregate,
                                 'description': ds.description,
                                 'tags': ds.tags})
        datasets.sort(key=lambda x: x['name'])
        result = {}
        result['datasets'] = datasets
        self.render_json(result)

add_route(Description, '/api/description.json')
