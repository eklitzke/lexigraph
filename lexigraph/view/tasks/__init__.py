import time
from google.appengine.api.labs import taskqueue

from lexigraph.handler import RequestHandler
from lexigraph.model import *

class TaskRequestHandler(RequestHandler):

    def initialize(self, request, response):
        super(TaskRequestHandler, self).initialize(request, response)
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        
class WorkFinished(Exception):
    def __init__(self, params={}):
        self.params = params

class TimedTaskHandler(TaskRequestHandler):

    TARGET_ELAPSED = 20.0

    def do_piece(self):
        pass

    def remaining_params(self):
        raise NotImplementedError

    def before_work(self):
        pass

    def post(self):
        self.before_work()
        time_end = time.time() + self.TARGET_ELAPSED
        params = None
        more_work = False
        try:
            while True:
                self.do_piece()
                if time.time() > time_end:
                    break
        except WorkFinished:
            pass

        if more_work:
            taskqueue.add(url=self.request.path, params=self.remaining_params())

import lexigraph.view.tasks.trim_series
