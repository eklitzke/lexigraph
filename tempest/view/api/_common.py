from django.utils import simplejson
from functools import wraps

from tempest.handler import RequestHandler
from tempest.model import *

class ApiException(Exception):
    pass

class MissingApiParam(ApiException):
    pass

def encode_json(func):
    @wraps(func)
    def inner(self):
        self.response.out.write(simplejson.dumps(func(self)))
    return inner

class ApiRequestHandler(RequestHandler):

    def initialize(self, request, response):
        super(RequestHandler, self).initialize(request, response)
        response.headers['Content-Type'] = 'application/json; charset=us-ascii'

    def fetch_data_set(self):
        data_set_id = self.request.get('data_set_id')
        data_set_name = self.request.get('data_set_name')

        if data_set_id is None and data_set_name is None:
            raise MissingApiParam

        if data_set_id:
            return DataSet.get_by_id(int(data_set_id))
        else:
            return DataSet.all().filter('name =', data_).fetch(1)
