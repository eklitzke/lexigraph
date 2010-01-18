from lexigraph.view import add_route
from lexigraph.handler import RequestHandler, requires_login
from google.appengine.api.users import create_logout_url

class Logout(RequestHandler):

    @requires_login #heh
    def get(self):
        self.redirect(create_logout_url('/'), permanent=False)

add_route(Logout, '/logout')
