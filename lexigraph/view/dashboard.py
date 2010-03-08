from lexigraph.view import add_route
from lexigraph.handler import TagsMixin, InteractiveHandler
from lexigraph import model
from django.utils import simplejson

class Dashboard(TagsMixin, InteractiveHandler):

    requires_login = True

    def get(self):
        if self.account is None:
            self.log.info('No accounts set up for user, redirecting')
            self.redirect('/account')
            return
        self.load_prefs()
        self.env['groups'] = model.AccessGroup.groups_for_user(self.account)
        self.env['dashboard_graphs'] = self.datasets_by_tags(['dashboard'])
        self.render_template('dashboard.html')
        
add_route(Dashboard, '/dashboard')
