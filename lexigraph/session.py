import datetime
import pickle
from google.appengine.ext import db

from lexigraph.log import ClassLogger
from lexigraph.model import LexigraphModel
from lexigraph.model.query import *
from lexigraph.cache import CacheDict

class SessionStorage(LexigraphModel):
    user_id = db.StringProperty(required=True)
    item_name = db.StringProperty(required=True)
    pickle = db.BlobProperty(required=True)
    timestamp = db.DateTimeProperty(required=True, auto_now_add=True)

    @classmethod
    def _remove_all(cls, worker):
        count = 0
        while True:
            rows = worker()
            if not rows:
                break
            count += len(rows)
            db.delete(rows)
        return count

    @classmethod
    def remove_expired(cls, expiration=3600):
        """Remove all expired rows."""
        cutoff = datetime.datetime.now() - datetime.timedelta(seconds=expiration)
        return cls._remove_all(lambda: fetch_all(cls.all().filter('timestamp <', cutoff)))

    @classmethod
    def remove_by_user(cls, user):
        """Remove all rows for a user."""
        user_id = user.user_id()
        return cls._remove_all(lambda: fetch_all(cls.all().filter('user_id =', user_id)))

class SessionCache(CacheDict):
    namespace = 'session'
    ttl = 90

    def __init__(self, user_id):
        self.user_id = user_id
        
    def _mangle(self, k):
        m = '%s:%s' % (self.user_id, k)
        self.log.info('mangled %r to %r' % (k, m))
        return m

class SessionState(object):

    log = ClassLogger()

    def __init__(self, user):
        self.user_id = user.user_id()
        self.cache = SessionCache(self.user_id)

    def query(self, key, many=False):
        q = SessionStorage.all().filter('user_id =', self.user_id).filter('item_name =', key)
        if many:
            return fetch_all(q)
        else:
            return maybe_one(q)

    def __getitem__(self, key):
        val = self.cache[key]
        if val is not None:
            self.log.info('HIT memcached for %s' % (key,))
            return val
        result = self.query(key)
        self.log.info('getitem query returned %s' % (result,))
        if result is not None:
            raw = pickle.loads(result.pickle)
            self.cache[key] = raw
            return raw

    def __delitem__(self, key):
        self.log.info('deleting %s' % (key,))
        del self.cache[key]
        db.delete(self.query(key, many=True))

    def delete(self, k):
        del self[k]

    def __setitem__(self, key, val):
        self.log.info('setting: %s = %s' % (key, val))
        SessionStorage(user_id=self.user_id, item_name=key, pickle=pickle.dumps(val, protocol=pickle.HIGHEST_PROTOCOL)).put()
        self.cache[key] = val
