from lexigraph.view import add_route
from lexigraph.handler import SessionHandler, InteractiveHandler
from lexigraph.model.db.prefs import Preference, UserPrefs

class UpdatePrefs(SessionHandler):

    requires_login = True

    def post(self):
        name = self.form_required('name')
        value = self.form_required('value')
        if name not in Preference.pref_names:
            self.render_json({'status': 1, 'msg': 'no such preference'})
            return
        UserPrefs.store_preference(self.user.user_id(), name, value)
        self.render_json({'status': 0})

class Prefs(InteractiveHandler):

    requires_login = True

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
add_route(UpdatePrefs, '/ajax/prefs')
