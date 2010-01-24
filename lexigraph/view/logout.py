from lexigraph.view import add_route
from lexigraph.handler import SessionHandler
from google.appengine.api.users import create_logout_url

class Logout(SessionHandler):

    def get(self):
        if self.user:
            self.session.clear_all()
            self.redirect(create_logout_url('/'), permanent=False)
        else:
            self.redirect('/', permanent=False)

add_route(Logout, '/logout')
