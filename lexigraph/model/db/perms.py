from functools import wraps

from google.appengine.ext import db
from google.appengine.api import users

from lexigraph.cache import surrogate_key, CacheDict
from lexigraph.model.db import APIError, LexigraphModel

#                            ,----> User
#                           /
# DataACL <---> ACLGroup <-+
#                          \
#                           `----> APIKey

class PermissionsError(APIError):
    pass

class PermissionsCache(CacheDict):
    namespace = 'permissions_cache'

def permissions_cache(func):
    @wraps(func)
    def inner(*args, **kwargs):
        key = surrogate_key(*args, **kwargs)

        cache = PermissionsCache()
        cache.namespace += func.__name__
        
        val = cache[key]
        if val is None:
            val = func(*args, **kwargs)
            if val is not None:
                cache[key] = val
        return val
    return inner

class ACLGroup(LexigraphModel):
    name = db.StringProperty(required=True) # unique

    # XXX: this may have a race conditions, since they use list properties.
    users = db.ListProperty(users.User)

    @classmethod
    @permissions_cache
    def groups_for_user(cls, user):
        return cls.all().filter('users =', user).fetch(30)

    @classmethod
    @permissions_cache
    def groups_for_api_key(cls, api_key):
        return APIKey.all().filter('group =', self).fetch(1)

class APIKey(LexigraphModel):
    group = db.ReferenceProperty(ACLGroup, required=True)
    token = db.StringProperty(required=True)

    @classmethod
    def create_new(cls, group=None):
        token = os.urandom(16).encode('hex')
        return cls(group=group, token=token)
