import time
import datetime

from google.appengine.ext import db

from tempest.log import ClassLogger
from tempest.model.util import to_python

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

class TempestModel(db.Model):

    log = ClassLogger()

    def to_python(self):
        d = {'id': self.key().id(), 'kind': self.__class__.__name__}
        for k in self.properties().iterkeys():
            d[k] = getattr(self, k)
        return to_python(d)

class DataSet(TempestModel):
    name = db.StringProperty(required=True) # unique
    aggregate = db.IntegerProperty(required=True)
    attributes = db.StringListProperty() # optional

    def add_points(self, value, timestamp):
        for schema in SeriesSchema.all().filter('data_set =', self):
            schema.add_point(value, timestamp)

class SeriesSchema(TempestModel):
    data_set = db.ReferenceProperty(DataSet, required=True)
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

        last_point.coalesce_value(self.data_set.aggregate, value, timestamp)
        return last_point

class DataPoint(TempestModel):
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
