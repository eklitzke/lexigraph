import time
import math
from collections import defaultdict

from google.appengine.api import users

from lexigraph import config
from lexigraph.view import add_route
from lexigraph.view.api._common import *
from lexigraph.handler import SessionHandler

from lexigraph import model

class Description(ApiRequestHandler, SessionHandler):
    """Returns a JSON description of available entities in the API."""

    def get_worker(self):

        def render_user(user):
            return {'nickname': user.nickname(), 'email': user.email()}

        result = {}
        datasets = []
        for ds in model.DataSet.all().filter('account =', self.account):
            access = ds.get_access(api_key=self.key)
            if access['read']:
                entry = {'key': ds.encode(),
                         'hostname': ds.hostname,
                         'permissions': access,
                         'name': ds.name,
                         'aggregate': ds.aggregate,
                         'description': ds.description,
                         'tags': ds.tags,
                         'series': []} 
                for series in DataSeries.all().filter('dataset =', ds):
                    entry['series'].append({'key': series.encode(),
                                            'interval': series.interval,
                                            'max_age': series.max_age,
                                            'description': series.description})
                datasets.append(entry)
        datasets.sort(key=lambda x: x['name'])
        result['datasets'] = datasets
        result['account'] = {'name': self.account.name, 'owner': render_user(self.account.owner)}
        access_group = model.AccessGroup.group_for_api_key(self.key)
        result['access_group'] = {'name': access_group.name,
                                  #'users': [render_user(users.User.get_by_user_id(u)) for u in access_group.users]}
                                  }
        self.render_json(result)

add_route(Description, '/api/description.json')
