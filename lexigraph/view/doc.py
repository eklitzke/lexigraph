from lexigraph.view import add_route
from lexigraph.handler import InteractiveHandler

class Doc(InteractiveHandler):

    requires_login = True

    def get(self):
        self.render_template('doc.html')

add_route(Doc, '/doc')
