from django.utils import simplejson
from google.appengine.ext import db

from lexigraph import config
from lexigraph.model import maybe_one
from lexigraph.model.db import LexigraphModel

class Preference(object):
    """Registry for preferences. you should not invoke the constructor directly,
    use the .new() classmethod instead.
    """

    all_prefs = []
    pref_names = set()
    pref_map = {}

    def __init__(self, display, name, kind, default):
        self.display = display
        self.name = name
        self.kind = kind
        self.default = default
       
    def normalize(self, value):
        if self.kind == 'int':
            return int(value)
        elif self.kind == 'bool':
            return bool(value)
        else:
            raise KeyError

    @classmethod
    def new(cls, display, name, kind, default):
        if name in cls.pref_names:
            raise ValueError
        obj = cls(display, name, kind, default)
        cls.all_prefs.append(obj)
        cls.pref_names.add(name)
        cls.pref_map[name] = obj
        return obj

    @classmethod
    def lookup(cls, name):
        return cls.pref_map[name]

    @classmethod
    def defaults(cls):
        return dict((p.name, p.default) for p in cls.all_prefs)

# Declared preferences go here
default_timespan = Preference.new('Default Timespan', 'default_timespan', 'int', config.default_timespan)
show_rollbar = Preference.new('Show Rollbar', 'show_rollbar', 'bool', False)
large_width = Preference.new('Graph Width (large)', 'large_width', 'int', 800)
small_width = Preference.new('Graph Width (small)', 'small_width', 'int', 400)

default_series_interval = Preference.new('default series interval', 'default_series_interval', 'int', 60)
default_series_maxage = Preference.new('default series max-age', 'default_series_maxage', 'int', 86400)

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
        db.delete(cls.pref_query(user_id, pref_name))
        p = Preference.lookup(pref_name)
        value = p.normalize(value)
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
            for row in cls.all().filter('user_id =', user_id):
                if row.pref_name not in Preference.pref_names:
                    self.log.warning('encountered unknown preference %s' % (row.pref_name,))
                    continue
                pref_dict[str(row.pref_name)] = simplejson.loads(row.value)
        return pref_dict
