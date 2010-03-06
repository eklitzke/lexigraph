from lexigraph.handler import RequestHandler
from lexigraph.model import *

class TaskRequestHandler(RequestHandler):

    def initialize(self, request, response):
        super(TaskRequestHandler, self).initialize(request, response)
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'

class TimedIdempotentTask(RequestHandler):

    batch_size = 100


    def pre_run(self):
        pass

    def run(self):
        self.pre_run()
        if not hasattr(self, 'items'):
            raise AttributeError("Missing attribute 'items'")
        self.items = list(self.items)
        while True:
            self.process_items(self.items[:self.batch_size])
            self.items = self.items[self.batch_size:]
            if not self.items:
                break
        self.post_run()

    def post_run(self):
        pass

    def process_item(self, item):
        raise NotImplementedError

    def process_items(self, items):
        pass


import lexigraph.view.tasks.trim_series
