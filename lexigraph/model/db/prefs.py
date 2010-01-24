from django.utils import simplejson
from google.appengine.ext import db

from lexigraph import config
from lexigraph.model.query import maybe_one, fetch_all
from lexigraph.model.db import LexigraphModel

class Preference(object):
    """Registry for preferences. you should not invoke the constructor directly,
    use the .new() classmethod instead.
    """

    all_prefs = []
    pref_names = set()

    def __init__(self, display, name, kind, default):
        self.display = display
        self.name = name
        self.kind = kind
        self.default = default

    @classmethod
    def new(cls, display, name, kind, default):
        if name in cls.pref_names:
            raise ValueError
        obj = cls(display, name, kind, default)
        cls.all_prefs.append(obj)
        cls.pref_names.add(name)

    @classmethod
    def defaults(cls):
        return dict((p.name, p.default) for p in cls.all_prefs)

# Declared preferences go here
Preference.new('Default Timespan', 'default_timespan', 'int', config.default_timespan)
Preference.new('Show Rollbar', 'show_rollbar', 'bool', False)
Preference.new('Graph Width (large)', 'large_width', 'int', 800)
Preference.new('Graph Width (small)', 'small_width', 'int', 400)

class UserPrefs(LexigraphModel):
    user_id = db.StringProperty(required=True)
    pref_name = db.StringProperty(required=True)
    value = db.StringProperty(required=True) # encoded as JSON

    @classmethod
    def pref_query(cls, user_id, pref_name):
        assert pref_name in Preference.pref_names
        return cls.all().filter('user_id =', user_id).filter('pref_name =', pref_name)

    @classmethod
    def store_preference(cls, user_id, pref_name, value):
        # need to clear any existing rows
        db.delete(fetch_all(cls.pref_query(user_id, pref_name)))
        serialized = simplejson.dumps(value)
        cls(user_id=user_id, pref_name=pref_name, value=serialized).put()

    @classmethod
    def get_preference(cls, user_id, pref_name):
        row = maybe_one(cls.pref_query(user_id, pref_name))
        if row:
            return simplejson.loads(row.value)
        else:
            return cls.all_prefs[pref_name]

    @classmethod
    def load_by_user_id(cls, user_id):
        pref_dict = Preference.defaults()
        if user_id:
            for row in fetch_all(cls.all().filter('user_id =', user_id)):
                if row.name not in Preference.pref_names:
                    self.log.warning('encountered unknown preference %s' % (row.name,))
                    continue
                pref_dict[str(row.pref_name)] = simplejson.loads(row.value)
        return pref_dict
