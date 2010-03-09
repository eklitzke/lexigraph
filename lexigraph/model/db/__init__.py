import os
import datetime
from django.utils import simplejson

from google.appengine.ext import db
from google.appengine.api import users

from lexigraph.log import ClassLogger
import lexigraph.crypt

Error = db.Error

class APIError(Exception):
    pass

class LexigraphModel(db.Model):

    log = ClassLogger()

    def __str__(self):
        return '%s(%s)' % (self.kind(), ', '.join('%s=%r' % (k, getattr(self, k)) for k in self.properties().keys()))
    __repr__ = __str__

    def encode(self):
        if not hasattr(self, '_encoded_id'):
            self._encoded_id = lexigraph.crypt.encode(self.key().id())
        return self._encoded_id

    @classmethod
    def decode(cls, encid):
        return cls.get_by_id(lexigraph.crypt.decode(encid))

class PermissionsError(APIError):
    pass

class Account(LexigraphModel):
    """A hosted lexigraph account."""
    name = db.StringProperty(required=True) # unique
    owner = db.UserProperty(required=True)

    @classmethod
    def by_user(cls, user):
        user_id = user.user_id()
        accounts = set()
        for row in AccessGroup.all().filter('users =', user_id):
            accounts.add(row.account)
        return sorted(accounts, key=lambda x: x.name)

    @classmethod
    def create(cls, name, owner):
        # ensure that the name is unique
        existing = maybe_one(cls.all().filter('name =', name))
        if existing:
            raise ValueError('Account with name %r already exists: %s' % (name, existing))

        obj = cls(name=name, owner=owner)
        obj.put()

        # now, create an access group
        group = AccessGroup.new('admin', obj, users=[owner])
        group.put()

        return obj

    def datasets(self):
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

class DataSet(LexigraphModel):
    # PK is (account, name)
    name = db.StringProperty(required=True) # unique
    aggregate = db.StringProperty(required=True)
    account = db.ReferenceProperty(Account, required=True)
    description = db.TextProperty()
    tags = db.StringListProperty() # optional

    @classmethod
    def from_encoded(cls, key, user=None, api_key=None, read=True, write=False, delete=False):
        if not (user or api_key):
            raise TypeError("Must specify a user or api_key")
        ds = cls.decode(key)
        if ds is None:
            cls.log.info('No dataset known by key %r' % (key,))
            return None
        if not ds.is_allowed(user=user, api_key=api_key, read=read, write=write, delete=delete):
            cls.log.info('Insufficient privileges by user=%r, api_key=%r' % (user, api_key))
            return None
        return ds

    def series(self):
        return DataSeries.all().filter('dataset =', self)

    def anonymous_permission(self):
        access = maybe_one(AccessControl.all().filter('dataset =', self))
        if access:
            return access
        else:
            self.log.warning('No anonymous AccessControl configured for %s' % (self,))
            return AccessControl.new(None, self)

    def is_allowed(self, user=None, api_key=None, read=False, write=False, delete=False):

        def check_group(group):
            if not group:
                return False
            access = maybe_one(AccessControl.all().filter('access_group =', group).filter('dataset =', self))
            return access and access.is_allowed(read=read, write=write, delete=delete)

        if self.anonymous_permission().is_allowed(read=read, write=write, delete=delete):
            return True

        if api_key:
            return check_group(AccessGroup.group_for_api_key(api_key))

        if user:
            return any(check_group(g) for g in AccessGroup.get_groups_for_user(self.account, user))

        return False

    def add_points(self, value, timestamp=None):
        """Add points to a DataSet. Authentication to do the add should be done
        higher up.
        """
        if timestamp is None:
            timestamp = datetime.datetime.now()
        series = self.series()
        for schema in series:
            schema.add_point(value, timestamp)

    def keys_json(self):
        """For compatibility with CompositeDataSet"""
        return simplejson.dumps([self.encode()]).strip()

class AccessControl(LexigraphModel):
    # The primary key is (access_group, dataset). The access_group may be None,
    # in which case it refers to the default set of access controls.
    access_group = db.ReferenceProperty(AccessGroup)
    dataset = db.ReferenceProperty(DataSet, required=True)

    readable = db.BooleanProperty(required=True)
    writable = db.BooleanProperty(required=True)
    deletable = db.BooleanProperty(required=True)

    @classmethod
    def new(cls, access_group, dataset, read=False, write=False, delete=False):
        # check the uniqueness constraint
        existing = maybe_one(cls.all().filter('access_group =', access_group).filter('dataset =', dataset))
        if existing:
            raise ValueError('An AccessControl already exists for (%s, %s)' % (access_group, dataset))
        return cls(access_group=access_group, dataset=dataset, readable=read, writable=write, deletable=delete)

    def is_allowed(self, read=False, write=False, delete=False):
        """Check if an AccessControl allows some action. For instance,
        obj.is_allowed(read=True) checks if the access control allows reading.
        """
        # should specify exactly one of read/write/delete
        assert int(read) + int(write) + int(delete) == 1
        if read:
            return self.readable
        elif write:
            return self.writable
        elif delete:
            return self.deletable

from lexigraph.model.db.prefs import *
from lexigraph.model.db.series import *
from lexigraph.model.db.tags import *
from lexigraph.model.db.composite import *
