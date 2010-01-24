from lexigraph.view import add_route
from lexigraph.handler import InteractiveHandler, requires_login
from lexigraph.model.db.prefs import Preference

class Prefs(InteractiveHandler):

    @requires_login
    def get(self):
        my_prefs = self.load_prefs()
        defined_prefs = sorted(Preference.all_prefs, key=lambda x: x.display)

        all_prefs = []
        for pref in defined_prefs:
            d = {'ref': pref, 'mine': my_prefs[pref.name]}
            all_prefs.append(d)

            self.env['message'] = 'sorry, can\'t alter these yet'
        self.env['all_prefs'] = all_prefs
        self.render_template('prefs.html')

add_route(Prefs, '/prefs')
