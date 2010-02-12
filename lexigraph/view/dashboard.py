from lexigraph.view import add_route
from lexigraph.handler import InteractiveHandler
from lexigraph import model
from lexigraph.model.query import *

from lexigraph.view.graph import TagQueryCache

class Dashboard(InteractiveHandler):

    requires_login = True

    def get(self):
        if self.account is None:
            self.log.info('No accounts set up for user, redirecting')
            self.redirect('/account')
            return
        self.load_prefs()
        self.env['groups'] = model.AccessGroup.groups_for_user(self.account)

        graph_names = TagQueryCache().select_by_tags(self.account, self.user, ['dashboard'])
        self.env['graphs'] = fetch_all(model.DataSet.all().filter('name IN', graph_names).order('name'))

        self.render_template('dashboard.html')
        
add_route(Dashboard, '/dashboard')
