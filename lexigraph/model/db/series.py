import time
import datetime

from google.appengine.ext import db

from lexigraph.cache import CacheDict
from lexigraph.model.db import LexigraphModel, DataSet

class _LastDataPointCache(CacheDict):
    
    namespace = 'lastdatapoint'

    def normalize_key(self, k):
        return str(k.key())
    normalize_val = normalize_key

    def last_datapoint(self, series):
        key = self[series]
        if key:
            return DataPoint.get_by_key_name(key)
        else:
            return DataPoint.all().filter('series =', series).order('-timestamp').fetch(1)

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
        self.log.debug('ts = %r' % (timestamp,))
        return int(timestamp / self.interval)

    def add_point(self, value, timestamp):
        last_point = LastDataPointCache.last_datapoint(self)

        if not last_point:
            # no data for the series yet, just add a new point
            return DataPoint(series=self, value=value).put()

        # is the point old?
        last_point, = last_point
        last_epoch = self.to_epoch(last_point.timestamp)
        curr_epoch = self.to_epoch(timestamp)

        # the point is for a new epoch, just add a new point
        if last_epoch != curr_epoch:
            last_point = DataPoint(series=self, value=value)
            last_point.put()
        else:
            last_point.coalesce_value(self.dataset.aggregate, value, timestamp)
 
        # TODO: only set when the value has changed
        LastDataPointCache[self] = last_point
        return last_point

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
