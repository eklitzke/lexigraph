import time
import datetime

from google.appengine.ext import db

from lexigraph.cache import CacheDict
from lexigraph.model.db import LexigraphModel, DataSet

class _LastDataPointCache(CacheDict):
    """A cache of the last point in a data series. This is pretty specialized
    and isn't intended to be used directly.
    """

    namespace = 'lastdatapoint_20100306c'

    def normalize_key(self, k):
        return k.key().id()

LastDataPointCache = _LastDataPointCache()


class DataSeries(LexigraphModel):
    dataset = db.ReferenceProperty(DataSet, required=True)
    interval = db.IntegerProperty(required=True)
    max_age = db.IntegerProperty()
    description = db.TextProperty()

    def to_epoch(self, timestamp):
        """timestamp: a unix timestamp"""
        if isinstance(timestamp, datetime.datetime):
            timestamp = time.mktime(timestamp.timetuple())
        return int(timestamp / self.interval)

    def add_point(self, value, timestamp):
        curr_epoch = self.to_epoch(timestamp)
        info = LastDataPointCache[self]

        def add_new_point():
            point = DataPoint(series=self, value=value, timestamp=timestamp)
            point.put()
            LastDataPointCache[self] = (point.key().id(), value, timestamp)

        if info is None:
            last_point = DataPoint.all().filter('series =', self).order('-timestamp').fetch(1)
            if not last_point:
                # no data for the series yet, just add a new point
                return add_new_point()
            last_point, = last_point
            last_epoch = self.to_epoch(last_point.timestamp)
            if last_epoch != curr_epoch:
                return add_new_point()
            last_point.coalesce_value(self.dataset.aggregate, value, timestamp)
        else:
            entity_id, old_value, old_timestamp = info
            last_epoch = self.to_epoch(old_timestamp)
            if last_epoch != curr_epoch:
                add_new_point()
            else:
                DataPoint.fake_coalesce_value(entity_id, self.dataset.aggregate, old_value, value, timestamp)

    def trim_points(self, limit=None):
        """Trim old points. Returns True if there is more data to process, and
        False otherwise.
        """
        if not self.max_age:
            return False
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

    @staticmethod
    def choose_coalesced_value(aggregate, old_value, new_value):
        if aggregate == 'min':
            return min(old_value, new_value)
        elif aggregate == 'max':
            return max(old_value, new_value)
        elif aggregate == 'sum':
            return old_value + new_value
        elif aggregate == 'old':
            return old_value
        elif aggregate == 'new':
            return new_value
        else:
            raise NotImplementedError("Coalesce strategy %r not implemented" % (aggregate,))

    def update_point(self, value, timestamp=None, update_cache=True):
        self.value = value
        self.timestamp = timestamp or datetime.datetime.now()
        self.put()
        if update_cache:
            LastDataPointCache[self.series] = (self.key().id(), value, timestamp)

    def coalesce_value(self, aggregate, new_value, new_timestamp):
        chosen_value = self.choose_coalesced_value(aggregate, self.value, new_value)
        if chosen_value != self.value:
            return self.update_point(chosen_value, new_timestamp)

    @classmethod
    def fake_coalesce_value(cls, entity_id, aggregate, old_value, new_value, new_timestamp):
        chosen_value = cls.choose_coalesced_value(aggregate, old_value, new_value)
        if chosen_value != old_value:
            obj = cls.get_by_id(entity_id)
            if obj is None:
                raise ValueError("id %d does not correspond to a valid DataPoint" % (entity_id,))
            return obj.update_point(chosen_value, new_timestamp)
