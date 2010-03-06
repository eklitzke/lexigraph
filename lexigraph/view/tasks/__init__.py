from lexigraph.handler import RequestHandler
from lexigraph.model import *

class TaskRequestHandler(RequestHandler):

    def initialize(self, request, response):
        super(TaskRequestHandler, self).initialize(request, response)
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'

import lexigraph.view.tasks.trim_series
