from google.appengine.ext import db

class DataSet(db.Model):
    name = db.StringProperty(required=True) # unique
    aggregate = db.StringProperty(required=True)
    attributes = db.StringListProperty() # optional

class SeriesSchema(db.Model):
    data_set = db.ReferenceProperty(DataSet, required=True)
    interval = db.IntegerProperty(required=True)
    max_age = db.IntegerProperty()

class DataSeries(db.Model):
    series = db.ReferenceProperty(SeriesSchema, required=True)
    value = db.FloatProperty(required=True)
    timestamp = db.DateTimeProperty(required=True, auto_now_add=True)
