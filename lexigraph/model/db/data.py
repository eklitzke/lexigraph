from google.appengine.ext import db

from lexigraph.model.db import LexigraphModel
from lexigraph.model.db.perms import *

class AggregateType(object):
    MIN = 1
    MAX = 2
    SUM = 3
    AVG = 4
    OLD = 5
    NEW = 6

    @classmethod
    def from_string(cls, s):
        return getattr(cls, s.upper())


class DataSet(LexigraphModel):
    name = db.StringProperty(required=True) # unique
    aggregate = db.IntegerProperty(required=True)
    attributes = db.StringListProperty() # optional

    def add_points(self, value, timestamp, user=None, api_key=None):
        if user is None:
            user = users.get_current_user()

        assert not (user and api_key), 'Not allowed to have both user %r and api_key %r' % (user, api_key)

        if user is None and api_key is None:
            perms = DataACL.anonymous_acl(self)
        elif user:
            perms = DataACL.by_user(self, user)
        elif api_key:
            perms = DataACL.by_api_key(self, user)

        if 'write' not in perms:
            raise PermissionsError('user=%r api_key=%r lacked "write" capability for %s' % (user, api_key, self))

        return self._add_points(value, timestamp)


    def _add_points(self, value, timestamp):
        """Add points to a DataSet. This is a private method; the authentication
        to do the add should be done higher up.
        """
        for schema in SeriesSchema.all().filter('dataset =', self):
            schema.add_point(value, timestamp)

    def perms_for_user(self, user):
        # first check if this user explicitly has a permission for the dataset
        acl = maybe_one(DataACL.all().filter('dataset =', self).filter('user =', user))
        if acl:
            return acl

        # check the default permissions, if the previous query wasn't equivalent to that
        if user is not None:
            acl = maybe_one(DataACL.all().filter('dataset =', self).filter('user =', None))
            if acl:
                return acl

        self.log.warning('unexpectedly saw no permissions for %s' % (self,))
        return DataACL(dataset=self, perms=[])

class DataACL(LexigraphModel):
    # The tuple (group, dataset) is considered to be unique and represents the
    # "primary key". The group may be null, which represents the "default"
    # permissions for all entities (including unauthenticated, anonymous users).
    group = db.ReferenceProperty(ACLGroup)
    dataset = db.ReferenceProperty(DataSet, required=True)
    perms = db.StringListProperty(required=True)

    def is_allowed(self, action):
        return action in self.perms

    @classmethod
    @permissions_cache
    def anonymous_acl(cls, dataset):
        """Fetch the anonymous ACL for a dataset (creating one with no
        permissions if no ACL exists).
        """
        acl = maybe_one(cls.all().filter('dataset =', dataset).filter('group =', None))
        if acl:
            return acl

        self.log.warning('Curiously, no default ACL was found for dataset %s' % (dataset,))
        return cls(dataset=dataset, perms=[])

    @classmethod
    def _combined_acls(cls, dataset, obj, colname, group_cb):
        """Helper method for get_by_dataset_and_user and
        get_by_dataset_and_api_key. This makes a DataACL object with the
        permissions representing the aggregate of all other ACLs, plus the
        anonymous ACL for the dataset.
        """

        # if there's no user/api_key, use the anonymous acl
        if not obj:
            return cls.anonymous_acl(dataset)

        obj_acl = maybe_one(cls.all().filter('dataset =', dataset).filter(colname + ' =', obj))
        if obj_acl:
            return obj_acl

        anon_acl = cls.anonymous_acl(dataset)

        groups = group_cb(obj)
        other_acls = cls.all().filter('dataset =', dataset).filter('group IN', groups).fetch(1000)
        if other_acls:
            perms = set(anon_acl.perms)
            for other_acl in other_acls:
                perms |= set(other_acl.perms)
            return cls(dataset=dataset, perms=perms)
        return anon_acl

    @classmethod
    def by_user(cls, dataset, user=None, check_current=True):
        if user is None and check_current:
            user = users.get_current_user()
        return cls._combined_acls(dataset, user, 'user', ACLGroup.groups_for_user)

    @classmethod
    def by_api_key(cls, dataset, api_key):
        assert api_key
        return cls._combined_acls(dataset, api_key, 'api_key', ACLGroup.groups_for_api_key)

class SeriesSchema(LexigraphModel):
    dataset = db.ReferenceProperty(DataSet, required=True)
    interval = db.IntegerProperty(required=True)
    max_age = db.IntegerProperty()

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
                for point in points:
                    point.delete()

class DataPoint(LexigraphModel):
    series = db.ReferenceProperty(SeriesSchema, required=True)
    value = db.FloatProperty(required=True)
    timestamp = db.DateTimeProperty(required=True, auto_now_add=True)

    def coalesce_value(self, aggregate, new_value, new_timestamp):
        """Coalesce an existing DataPoint with a new value/timestamp"""

        def update_value(updated_value):
            self.log.debug('coalescing value for id=%s (%s, %s) -> (%s, %s)' % (self.key().id(), self.value, self.timestamp, updated_value, new_timestamp))
            self.value = updated_value
            self.timestamp = new_timestamp
            self.put()

        if aggregate == AggregateType.MIN:
            update_value(min(self.value, new_value))
        elif aggregate == AggregateType.MAX:
            update_value(max(self.value, new_value))
        elif aggregate == AggregateType.SUM:
            update_value(self.value + new_value)
        elif aggregate == AggregateType.AVG:
            raise NotImplementedError
        elif aggregate == AggregateType.OLD:
            update_value(self.value) # i.e. just update the timestamp
        elif aggregate == AggregateType.NEW:
            update_value(new_value)
