from lexigraph.view import add_route
from lexigraph.handler import InteractiveHandler, requires_login

class Doc(InteractiveHandler):

    @requires_login
    def get(self):
        self.render_template('doc.html')

add_route(Doc, '/doc')
