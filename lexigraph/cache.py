import pickle
import hashlib
from google.appengine.api import memcache
from lexigraph.log import ClassLogger

def surrogate_key(*args, **kwargs):
    """Take args and kwargs (from a function take *args, **kwargs) and turn them
    into a key suitable for usage with memcache.
    """

    def norm_surrogate_key(k):
        if isinstance(k, db.Model):
            surrogate_key.append(k.key().id())
        else:
            surrogate_key.append(k)

    surrogate = [norm_surrogate_key(arg) for arg in args]
    for k in sorted(kwargs.keys()):
        surrogate.extend([k, norm_surrogate_key(kwargs[k])])
    return surrogate

class CacheDict(object):

    namespace = 'cachedict'
    ttl = 0

    log = ClassLogger()

    def _mangle(self, k):
        k = self.normalize_key(k)
        return hashlib.sha1(pickle.dumps(k)).hexdigest()

    def normalize_key(self, k):
        return k

    def normalize_val(self, v):
        return v

    def __getitem__(self, k):
        k = self._mangle(k)
        return memcache.get(k, namespace=self.namespace)

    def __setitem__(self, k, v):
        k = self._mangle(k)
        v = self.normalize_val(v)
        memcache.set(k, v, time=self.ttl, namespace=self.namespace)

    def __delitem__(self, k):
        k = self._mangle(k)
        memcache.delete(k, namespace=self.namespace)
