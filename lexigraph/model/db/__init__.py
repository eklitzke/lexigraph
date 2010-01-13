from google.appengine.ext import db

from lexigraph.log import ClassLogger
from lexigraph.model.util import to_python

class APIError(Exception):
    pass

class LexigraphModel(db.Model):

    log = ClassLogger()

    def to_python(self):
        d = {'id': self.key().id(), 'kind': self.__class__.__name__}
        for k in self.properties().iterkeys():
            d[k] = getattr(self, k)
        return to_python(d)

from lexigraph.model.db.perms import *
from lexigraph.model.db.data import *
