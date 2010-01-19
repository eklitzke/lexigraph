from django.utils import simplejson
from functools import wraps

from lexigraph.handler import RequestHandler
from lexigraph.model import *

class ApiError(Exception):
    pass

class StatusCodes(object):

    OK = 0

    ALREADY_EXISTS = 100
    MISSING_FIELD  = 101
    INVALID_FIELD  = 102
    INVALID_TOKEN  = 103

def requires_api_key(func):
    @wraps(func)
    def inner(self):
        token = self.request.get('token')
        if not token:
            return self.make_error(MISSING_PARAM, {'field': 'token'})
        keys = ApiKey.all().query('token =', token).fetch(1)
        if not keys:
            return self.make_error(INVALID_TOKEN, {'field': 'token'})
        return func(self)

def encode_json(func):
    @wraps(func)
    def inner(self):
        val = func(self)
        self.log.debug('returning json representation of %r' % (val,))
        self.response.out.write(simplejson.dumps(val))
    return inner

class ApiRequestHandler(RequestHandler):

    def initialize(self, request, response):
        super(ApiRequestHandler, self).initialize(request, response)
        response.headers['Content-Type'] = 'application/json; charset=us-ascii'
    
    def process_form(self):
        self.key = self.request.get('key')

    def get_series(self):
        # if a series is specified, prefer that
        series = self.request.get('series')
        if series:
            return SeriesCache.lookup(series)

        # otherwise, try to do a dataset/interval combination
        dataset = self.request.get('dataset')
        interval = self.request.get('interval')
        if dataset and interval:
            return SeriesNamedCache.lookup(dataset, int(interval))

    def fetch_data_set(self):
        data_set_id = self.request.get('data_set_id')
        data_set_name = self.request.get('data_set_name')

        if data_set_id is None and data_set_name is None:
            raise MissingApiParam

        if data_set_id:
            return DataSet.get_by_id(int(data_set_id))
        else:
            return DataSet.all().filter('name =', data_).fetch(1)
    
    def make_error(self, code, **kw):
        return self.add_status({}, code, **kw)

    def add_status(self, response, code, **kw):
        self.response.headers['X-API-Status'] = str(code)
        response['status'] = kw.copy()
    	response['status']['code'] = code
        return response

    def get(self):
        assert hasattr(self, 'get_worker')
        self.process_form()
        self.get_worker()
