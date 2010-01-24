from lexigraph.view import add_route
from lexigraph.handler import RequestHandler, requires_login

class Prefs(RequestHandler):

    @requires_login
    def get(self):
        self.load_prefs()
        self.render_template('prefs.html')

add_route(Prefs, '/prefs')
