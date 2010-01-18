import datetime
from django.utils import simplejson 
from google.appengine.ext import db

from lexigraph.model import LexigraphModel
from lexigraph.model.query import *
from lexigraph.cache import CacheDict

class SessionStorage(LexigraphModel):
    user_id = db.StringProperty(required=True)
    item_name = db.StringProperty(required=True)
    json = db.TextProperty(required=True)
    timestamp = db.DateTimeProperty(required=True, auto_now_add=True)

    @classmethod
    def remove_expired(cls, expiration=3600):
        cutoff = datetime.datetime.now() - datetime.timedelta(seconds=expiration)
        count = 0
        while True:
            rows = fetch_all(cls.all().filter('timestamp <', cutoff))
            if not rows:
                break
            count += len(rows)
            for row in rows:
                row.delete()
        return count

class SessionCache(CacheDict):
    namespace = 'session'
    ttl = 90

    def __init__(self, user_id):
        self.user_id = user_id
        
    def _mangle(self, k):
        return '%s:%s' % (self.user_id, k)

class SessionState(object):

    def __init__(self, user):
        self.user_id = user.key().id()
        self.cache = SessionCache(self.user_id)

    def query(self, key):
        return maybe_one(SessionStorage.all().filter('user_id =', self.user_id).filter('item_name =', key))

    def __getitem__(self, key):
        val = self.cache[key]
        if val is not None:
            return val
        result = self.query(key)
        if result is not None:
            raw = simplejson.loads(result)
            self.cache[key] = raw
            return raw

    def __delitem__(self, key):
        del self.cache[key]
        row = self.query(key)
        if row:
            row.delete()

    def __setitem__(self, key, val):
        SessionStorage(user_id=self.user_id, item_name=key, json=simplejson.dumps(val)).put()
        self.cache[key] = val
