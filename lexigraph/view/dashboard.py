from lexigraph.view import add_route
from lexigraph.handler import InteractiveHandler, requires_login
from lexigraph import model
from lexigraph.model.query import *

class Dashboard(InteractiveHandler):

    def all_datasets(self):
        dataset_names = set()
        for group in self.env['groups']:
            rows = fetch_all(model.AccessControl.all().filter('access_group =', group).filter('readable =', True))
            for row in rows:
                try:
                    dataset_names.add(row.dataset.name)
                except model.Error:
                    pass
        return sorted(dataset_names)

    @requires_login
    def get(self):
        if self.account is None:
            self.log.info('No accounts set up for user, redirecting')
            self.redirect('/account')
            return
        self.load_prefs()
        self.env['groups'] = model.AccessGroup.groups_for_user(self.account)
        self.env['datasets'] = self.all_datasets()
        self.render_template('dashboard.html')
        
add_route(Dashboard, '/dashboard')
