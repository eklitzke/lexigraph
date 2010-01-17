from lexigraph.handler import RequestHandler
from google.appengine.api import users

class Manage(RequestHandler):

    def get(self):
        user = users.get_current_user()
        
        self.render_template('home.html')
        
__all__ = ['Home']
