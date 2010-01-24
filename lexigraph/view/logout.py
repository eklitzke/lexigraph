import lexigraph.session
from lexigraph.view import add_route
from lexigraph.handler import SessionHandler
from google.appengine.api.users import create_logout_url

class Logout(SessionHandler):

    def get(self):
        if self.user:
            lexigraph.session.SessionStorage.remove_by_user(self.user)
            self.redirect(create_logout_url('/'), permanent=False)
        else:
            self.redirect('/', permanent=False)

add_route(Logout, '/logout')
