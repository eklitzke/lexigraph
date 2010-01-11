import pickle
import hashlib
from google.appengine.api import memcache

class CacheDict(object):

    namespace = 'cachedict'
    ttl = 0

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
