import os

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache

from lexigraph.model.db import LexigraphModel
from lexigraph.model import maybe_one

class Account(LexigraphModel):
    """A hosted lexigraph account."""
    name = db.StringProperty(required=True) # unique, lowercase version of display_name
    display_name = db.StringProperty(required=True)
    owner = db.UserProperty(required=True)

    @classmethod
    def by_user(cls, user):
        user_id = user.user_id()
        accounts = set()
        for row in AccessGroup.all().filter('users =', user_id):
            accounts.add(row.account)
        return sorted(accounts, key=lambda x: x.name)

    @classmethod
    def create(cls, display_name, owner):
        # ensure that the name is unique
        name = display_name.lower()
        existing = maybe_one(cls.all().filter('name =', name))
        if existing:
            raise ValueError('Account with name %r already exists: %s' % (name, existing))

        obj = cls(name=name, display_name=display_name, owner=owner)
        obj.put()

        # now, create an access group
        group = AccessGroup.new('admin', obj, users=[owner])
        group.put()

        return obj

    def datasets(self):
        from lexigraph.model.db import DataSet
        return DataSet.all().filter('account =', self)

class AccessGroup(LexigraphModel):
    name = db.StringProperty(required=True) # unique
    account = db.ReferenceProperty(Account, required=True)
    api_token = db.StringProperty()
    users = db.StringListProperty(required=True)

    @classmethod
    def new(cls, name, account, api_key=True, users=[]):
        TOKEN_LENGTH = 16
        if api_key == True:
            api_token = os.urandom(TOKEN_LENGTH).encode('hex')
        elif api_key == False:
            api_token = None
        else:
            api_token = api_key
            assert type(api_token) is str
            assert len(api_token) == TOKEN_LENGTH
        return cls(name=name, account=account, api_token=api_token, users=[u.user_id() for u in users])

    @classmethod
    def groups_for_user(cls, account, user=None):
        if user is None:
            user = users.get_current_user()
            assert user is not None
        return cls.all().filter('account =', account).filter('users =', user.user_id())

    @classmethod
    def group_for_api_key(cls, api_token):
        return maybe_one(cls.all().filter('api_token =', api_token))

class ActiveAccount(LexigraphModel):
    """The active account for a user. This is stored separately from the session
    system since this must be persistent.
    """
    user = db.UserProperty(required=True)
    account = db.ReferenceProperty(Account, required=True)

    @classmethod
    def get_active_account(cls, user):
        user_id = user.user_id()
        account_id = memcache.get(user_id, namespace='active_account')
        if account_id:
            return Account.get_by_id(account_id)
        row = maybe_one(cls.all().filter('user =', user))
        if row:
            memcache.set(user_id, row.account.key().id(), namespace='active_account')
            return row.account
        else:
            return None

    @classmethod
    def set_active_account(cls, user, account):
        row = maybe_one(cls.all().filter('user =', user))
        if row:
            row.account = account
        else:
            cls(user=user, account=account).put()
        memcache.set(user.user_id(), account.key().id(), namespace='active_account')
