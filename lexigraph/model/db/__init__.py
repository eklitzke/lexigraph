import os
import time
import datetime

from google.appengine.ext import db
from google.appengine.api import users

from vendor.gaeutilities.rotmodel import ROTModel
from lexigraph.log import ClassLogger
from lexigraph.model.query import maybe_one, fetch_all
from lexigraph.model.util import to_python
from lexigraph import simplejson

Error = db.Error

class APIError(Exception):
    pass

class LexigraphModel(ROTModel):

    log = ClassLogger()

    def to_python(self):
        d = {'id': self.key().id(), 'kind': self.__class__.__name__}
        for k in self.properties().iterkeys():
            d[k] = getattr(self, k)
        return to_python(d)

    def __str__(self):
        return '%s(%s)' % (self.kind(), ', '.join('%s=%r' % (k, getattr(self, k)) for k in self.properties().keys()))
    __repr__ = __str__

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
        for row in fetch_all(AccessGroup.all().filter('users =', user_id)):
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
        return fetch_all(DataSet.all().filter('account =', self))

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
        return fetch_all(cls.all().filter('account =', account).filter('users =', user.user_id()))

    @classmethod
    def group_for_api_key(cls, api_token):
        return maybe_one(cls.all().filter('api_token =', api_token))

class DataSet(LexigraphModel):
    # PK is (account, name)
    name = db.StringProperty(required=True) # unique
    aggregate = db.StringProperty(required=True)
    account = db.ReferenceProperty(Account, required=True)
    tags = db.StringListProperty() # optional

    def series(self):
        return fetch_all(DataSeries.all().filter('dataset =', self))

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
        self.log.info('added points to %d series' % (len(series),))

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

class DataSeries(LexigraphModel):
    dataset = db.ReferenceProperty(DataSet, required=True)
    interval = db.IntegerProperty(required=True)
    max_age = db.IntegerProperty()
    description = db.TextProperty()

    def to_epoch(self, timestamp):
        """timestamp: a unix timestamp"""
        if isinstance(timestamp, datetime.datetime):
            timestamp = time.mktime(timestamp.timetuple())
        self.log.debug('ts = %r' % (timestamp,))
        return int(timestamp / self.interval)

    def add_point(self, value, timestamp):
        last_point = DataPoint.all().filter('series =', self).order('-timestamp').fetch(1)

        if not last_point:
            # no data for the series yet, just add a new point
            return DataPoint(series=self, value=value).put()

        # is the point old?
        last_point, = last_point
        last_epoch = self.to_epoch(last_point.timestamp)
        curr_epoch = self.to_epoch(timestamp)

        # the point is for a new epoch, just add a new point
        if last_epoch != curr_epoch:
            return DataPoint(series=self, value=value).put()

        last_point.coalesce_value(self.dataset.aggregate, value, timestamp)
        return last_point

    def trim_points(self, limit=1000):
        if not self.max_age:
            return
        max_age = datetime.datetime.now() - datetime.timedelta(seconds=self.max_age)
        points = True
        while points:
            points = DataPoint.all().filter('series =', self).filter('timestamp <', max_age).fetch(limit)
            if points:
                db.delete(points)

class DataPoint(LexigraphModel):
    series = db.ReferenceProperty(DataSeries, required=True)
    value = db.FloatProperty(required=True)
    timestamp = db.DateTimeProperty(required=True, auto_now_add=True)

    def coalesce_value(self, aggregate, new_value, new_timestamp):
        """Coalesce an existing DataPoint with a new value/timestamp"""

        def update_value(updated_value):
            self.log.debug('coalescing value for id=%s (%s, %s) -> (%s, %s)' % (self.key().id(), self.value, self.timestamp, updated_value, new_timestamp))
            self.value = updated_value
            self.timestamp = new_timestamp
            self.put()

        if aggregate == 'min':
            update_value(min(self.value, new_value))
        elif aggregate == 'max':
            update_value(max(self.value, new_value))
        elif aggregate == 'sum':
            update_value(self.value + new_value)
        #elif aggregate == AggregateType.AVG:
        #    raise NotImplementedError
        elif aggregate == 'old':
            update_value(self.value) # i.e. just update the timestamp
        elif aggregate == 'new':
            update_value(new_value)
        else:
            raise NotImplementedError

class UserPrefs(LexigraphModel):
    user_id = db.StringProperty(required=True)
    pref_name = db.StringProperty(required=True)
    value = db.StringProperty(required=True) # encoded as JSON

    # defines valid preferences, along with their default value
    all_prefs = {
        'show_rollbar': False,
        'large_height': 800
    }

    @classmethod
    def pref_query(cls, user_id, pref_name):
        assert pref_name in cls.all_prefs
        return cls.all().filter('user_id =', user_id).filter('pref_name =', pref_name)

    @classmethod
    def store_preference(cls, user_id, pref_name, value):
        # need to clear any existing rows
        db.delete(fetch_all(cls.pref_query(user_id, pref_name)))
        serialized = simplejson.dumps(value)
        cls(user_id=user_id, pref_name=pref_name, value=serialized).put()

    @classmethod
    def get_preference(cls, user_id, pref_name):
        row = maybe_one(cls.pref_query(user_id, pref_name))
        if row:
            return simplejson.loads(row.value)
        else:
            return cls.all_prefs[pref_name]

    @classmethod
    def load_by_user_id(cls, user_id):
        pref_dict = cls.all_prefs.copy()
        if user_id:
            for row in fetch_all(cls.all().filter('user_id =', user_id)):
                pref_dict[str(row.pref_name)] = simplejson.loads(row.value)
        return pref_dict
