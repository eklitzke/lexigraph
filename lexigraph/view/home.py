from lexigraph.view import add_route
from lexigraph.handler import InteractiveHandler

class Home(InteractiveHandler):

    def get(self):
        if self.request.path != '/':
            self.redirect('/')
            return
        self.env['use_ssl'] = False
        self.render_template('home.html')

add_route(Home, '/')
