from lexigraph.view import add_route
from lexigraph.handler import RequestHandler, requires_login

class Prefs(RequestHandler):

    @requires_login
    def get(self):
        self.redirect('/dashboard')

add_route(Prefs, '/prefs')
