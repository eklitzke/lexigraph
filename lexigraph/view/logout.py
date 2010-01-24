import lexigraph.session
from lexigraph.view import add_route
from lexigraph.handler import SessionHandler, requires_login
from google.appengine.api.users import create_logout_url

class Logout(SessionHandler):

    @requires_login #heh
    def get(self):
        lexigraph.session.SessionStorage.remove_by_user(self.user)
        self.redirect(create_logout_url('/'), permanent=False)

add_route(Logout, '/logout')
