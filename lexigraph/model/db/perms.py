from google.appengine.ext import db
from google.appengine.api import users

from lexigraph.model.db import LexigraphModel

#                            ,----> User
#                           /
# DataACL <---> ACLGroup <-+
#                          \
#                           `----> APIKey


class ACLGroup(LexigraphModel):
    name = db.StringProperty(required=True) # unique

    # XXX: this may have a race conditions, since they use list properties.
    users = db.ListProperty(users.User)

    @classmethod
    def groups_for_user(cls, user):
        return cls.all().filter('users =', user).fetch(30)

    @classmethod
    def groups_for_api_key(cls, api_key):
        return APIKey.all().filter('group =', self).fetch(1)

class APIKey(LexigraphModel):
    group = db.ReferenceProperty(ACLGroup, required=True)
    token = db.StringProperty(required=True)

    @classmethod
    def create_new(cls, group=None):
        token = os.urandom(16).encode('hex')
        return cls(group=group, token=token)
