from lexigraph.view import add_route
from lexigraph.handler import InteractiveHandler
from lexigraph import model
from lexigraph.model.query import *

class Dashboard(InteractiveHandler):

    requires_login = True

    def get(self):
        if self.account is None:
            self.log.info('No accounts set up for user, redirecting')
            self.redirect('/account')
            return
        self.load_prefs()
        self.env['groups'] = model.AccessGroup.groups_for_user(self.account)
        self.render_template('dashboard.html')
        
add_route(Dashboard, '/dashboard')
