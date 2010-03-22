import os
import datetime
from django.utils import simplejson

from google.appengine.ext import db
from google.appengine.api import users

from lexigraph.log import ClassLogger
from lexigraph.model import maybe_one
import lexigraph.crypt

Error = db.Error

class APIError(Exception):
    pass

class LexigraphModel(db.Model):
    """The base class for all lexigraph models."""

    log = ClassLogger()

    def __str__(self):
        return '%s(%s)' % (self.kind(), ', '.join('%s=%r' % (k, getattr(self, k)) for k in self.properties().keys()))
    __repr__ = __str__

    def encode(self):
        """Get the encoded (encrypted) id for a model instance."""
        if not hasattr(self, '_encoded_id'):
            self._encoded_id = lexigraph.crypt.encode(self.key().id())
        return self._encoded_id

    @classmethod
    def decode(cls, encid):
        """Load a model instance from its encoded id."""
        return cls.get_by_id(lexigraph.crypt.decode(encid))

class PermissionsError(APIError):
    pass

from lexigraph.model.db.account import *
from lexigraph.model.db.host import *

class DataSet(LexigraphModel):
    # PK is (account, name)
    name = db.StringProperty(required=True) # unique
    hostname = db.StringProperty() # unique
    aggregate = db.StringProperty(required=True)
    account = db.ReferenceProperty(Account, required=True)
    description = db.TextProperty()
    scale = db.FloatProperty()
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

    @classmethod
    def from_string(cls, account, string, user=None, api_key=None, read=True, write=False, delete=False):
        """Make a best effort attempt to try to turn a string into a valid
        dataset for a user. We don't know if the string represents an encoded
        key, or if it's the name of a dataset.
        """
        if not (user or api_key):
            raise TypeError("Must specify a user or api_key")

        if len(string) == 22:
            ds = cls.from_encoded(string, user=user, api_key=api_key, read=read, write=write, delete=delete)
            if ds:
                return ds

        def check_row(row):
            if row.is_allowed(user=user, api_key=api_key, read=read, write=write, delete=delete):
                return row
            else:
                return None

        if ':' in name:
            hostname, name = name.split(':', 1)
            row = maybe_one(cls.all().filter('account =', account).filter('hostname =', hostname).filter('name =', name))
            if row:
                return check_row(row)

        rows = cls.all().filter('account =', account).filter('name =', name).fetch(2)
        if not rows:
            return None
        if len(rows) == 1:
            return check_row(rows[0])
        else:
            # there are multiple rows. the name is allowed *only* if exactly one row has the correct permissions
            allowed = []
            for row in rows:
                row = check_row(row)
                if row:
                    allowed.append(row)
            if len(allowed) == 1:
                return allowed[0]
            else:
                return None

    def series(self):
        return DataSeries.all().filter('dataset =', self)

    def anonymous_permission(self):
        access = maybe_one(AccessControl.all().filter('dataset =', self))
        if access:
            return access
        else:
            self.log.warning('No anonymous AccessControl configured for %s' % (self,))
            return AccessControl.new(None, self)

    def get_access(self, user=None, api_key=None):
        """Get the access rights for a user/api_key. This will be a dictionary
        with three keys (read, write, delete) and values will be bools.
        """
        assert user or api_key
        access = self.anonymous_permission().get_access()

        def merge_access(group):
            if not group:
                return access
            other = maybe_one(AccessControl.all().filter('access_group =', group).filter('dataset =', self))
            if not other:
                return access
            return {'read': access['read'] or other['read'],
                    'write': access['write'] or other['write'],
                    'delete': access['delete'] or other['delete']}

        if api_key:
            access = merge_access(AccessGroup.group_for_api_key(api_key))

        if user:
            for g in AccessGroup.groups_for_user(self.account, user):
                access = merge_access(g)
        return access


    def is_allowed(self, user=None, api_key=None, read=False, write=False, delete=False):
        access = self.get_access(user=user, api_key=api_key)
        if read and not access['read']:
            return False
        if write and not access['write']:
            return False
        if delete and not access['delete']:
            return False
        return True

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

    def as_dict(self):
        return {'name': self.name,
                'key': self.encode(),
                'hostname': self.hostname,
                'aggregate': aggregate,
                'tags': self.tags}

    def as_json(self):
        return simplejson.dumps(self.as_dict())

class AccessControl(LexigraphModel):
    # The primary key is (access_group, dataset). The access_group may be None,

    def as_json(self):
        """This is a minimal json representation of the dataset. The intention
        is that this may be embedded into HTML pages.
        """
        return simplejson.dumps({'name': self.name,
                                 'key': self.encode(),
                                 'hostname': self.hostname,
                                 'aggregate': aggregate,
                                 'tags': self.tags})

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
        # should specify at least one of read/write/delete
        if not (read or write or delete):
            raise ValueError('Must specify at least one of read/write/delete')
        if read and not self.readable:
            return False
        if write and not self.writable:
            return False
        if delete and not self.deletable:
            return False
        return True

    def get_access(self):
        return {'read': self.readable, 'write': self.writable, 'delete': self.deletable}

from lexigraph.model.db.prefs import *
from lexigraph.model.db.series import *
from lexigraph.model.db.tags import *
from lexigraph.model.db.composite import *
