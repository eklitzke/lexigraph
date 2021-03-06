import datetime
import pickle
from google.appengine.ext import db

from lexigraph.log import ClassLogger
from lexigraph.model import maybe_one, LexigraphModel
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
            rows = list(worker())
            if not rows:
                break
            count += len(rows)
            db.delete(rows)
        return count

    @classmethod
    def remove_expired(cls, expiration=6*3600):
        """Remove all expired rows."""
        cutoff = datetime.datetime.now() - datetime.timedelta(seconds=expiration)
        return cls._remove_all(lambda: cls.all().filter('timestamp <', cutoff))

class SessionCache(CacheDict):
    namespace = 'session'
    ttl = 90

    def __init__(self, user_id):
        self.user_id = user_id

    def _mangle(self, k):
        return '%s:%s' % (self.user_id, k)

class SessionState(object):

    log = ClassLogger()

    def __init__(self, user_id):
        self.user_id = user_id
        self.cache = SessionCache(user_id)

    def query(self, key, many=False):
        q = SessionStorage.all().filter('user_id =', self.user_id).filter('item_name =', key)
        if many:
            return list(q)
        else:
            return maybe_one(q)

    def get_once(self, key, default_value=None):
        """Read a value out of the session state, and delete it if a value was
        read. This is useful for "read once" data like the flash messages.

        Logically this is equivalent to, but better optimized than:
          val = session[key] or default_value
          del session[key]
        """
        val = self.cache[key]
        if val is not None:
            self.log.debug('hit session cache for key=%r' % (key,))
            self.delete(key, delete_cache=True)
            return val

        # XXX: the use case for this is really just for the "flash" messages, so
        # really if the cache misses, we shouldn't even bother with the database
        # work

        result = self.query(key)
        if result is not None:
            self.log.info('hit db')
            raw = pickle.loads(result.pickle)
            result.delete()
            return raw

        return default_value

    def __getitem__(self, key):
        val = self.cache[key]
        if val is not None:
            return val
        result = self.query(key)
        if result is not None:
            raw = pickle.loads(result.pickle)
            self.cache[key] = raw
            return raw

    def delete(self, key, delete_cache=True, ignore_db_errors=True):
        if delete_cache:
            del self.cache[key]

        try:
            db.delete(SessionStorage.all().filter('user_id =', self.user_id).filter('item_name =', key))
        except db.BadKeyError:
            if ignore_db_errors:
                self.log.warning("Ignoring missing session key for user_id=%d, item_name=%r" % (self.user_id, key))
            else:
                raise

    def __delitem__(self, key):
        self.delete(key)

    def __setitem__(self, key, val):
        SessionStorage(user_id=self.user_id, item_name=key, pickle=pickle.dumps(val, protocol=pickle.HIGHEST_PROTOCOL)).put()
        self.cache[key] = val

    def clear_all(self):
        rows = SessionStorage.all().filter('user_id =', self.user_id)
        for row in rows:
            del self.cache[row.item_name]
        db.delete(rows)
