from lexigraph.model.db import LexigraphModel, Account
from google.appengine.ext import db
from django.utils import simplejson

# TODO add permissions
class CompositeDataSet(LexigraphModel):
    names = db.StringListProperty(required=True)
    tags = db.StringListProperty()
    account = db.ReferenceProperty(Account, required=True)

    def names_json(self):
        return simplejson.dumps(list(self.names)).strip()
