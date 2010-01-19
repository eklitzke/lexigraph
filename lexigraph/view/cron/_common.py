from lexigraph.handler import RequestHandler
from lexigraph.model import *

class CronRequestHandler(RequestHandler):
    def initialize(self, request, response):
        super(CronRequestHandler, self).initialize(request, response)
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'
