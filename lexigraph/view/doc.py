from lexigraph.view import add_route
from lexigraph.handler import RequestHandler

class Doc(RequestHandler):

    # no login required!
    def get(self):
        self.render_template('doc.html')

add_route(Doc, '/doc')
