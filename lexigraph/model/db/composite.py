from lexigraph.model.db import LexigraphModel, Account
from google.appengine.ext import db
from lexigraph.model.db import DataSet
from django.utils import simplejson

# TODO add permissions
class CompositeDataSet(LexigraphModel):
    names = db.StringListProperty(required=True)
    tags = db.StringListProperty()
    account = db.ReferenceProperty(Account, required=True)

    def keys_json(self):
        keys = []
        for ds in DataSet.all().filter('account =', self.account).filter('name IN', self.names):
            keys.append(ds.encode())
        return simplejson.dumps(keys)
