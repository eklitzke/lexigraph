import datetime
from lexigraph.view import add_route
from lexigraph.handler import InteractiveHandler

class ShowUnixtime(InteractiveHandler):

    def initialize(self, request, response):
        super(ShowUnixtime, self).initialize(request, response)
        response.headers['Content-Type'] = 'text/plain'

    def get(self):
        self.response.out.write(datetime.datetime.now().strftime('%s'))

add_route(ShowUnixtime, '/debug/unixtime')
