from lexigraph.model.db import LexigraphModel, Account
from google.appengine.ext import db
from lexigraph.model.db import DataSet
from django.utils import simplejson

# TODO add permissions
class CompositeDataSet(LexigraphModel):
    name = db.StringProperty()
    names = db.StringListProperty(required=True)
    tags = db.StringListProperty()
    account = db.ReferenceProperty(Account, required=True)

    @classmethod
    def create(cls, name, names, account, tags):
        # ensure the uniqueness of [account, names]
        names_set = set(names)
        for cds in cls.all().filter('account =', account):
            if set(cds.names) == names_set:
                raise ValueError
        return cls(name=name, names=names, account=account, tags=tags)

    @classmethod
    def from_encoded(cls, key, user=None, api_key=None, read=True, write=False, delete=False):
        if not (user or api_key):
            raise TypeError("Must specify a user or api_key")
        cds = cls.decode(key)
        if cds is None:
            cls.log.info('No dataset known by key %r' % (key,))
            return None
        if not cds.is_allowed(user=user, api_key=api_key, read=read, write=write, delete=delete):
            cls.log.info('Insufficient privileges by user=%r, api_key=%r' % (user, api_key))
            return None
        return cds

    def is_allowed(self, user=None, api_key=None, read=False, write=False, delete=False):
        for ds in DataSet.all().filter('account =', self.account).filter('name IN', self.names):
            if not ds.is_allowed(user=user, api_key=api_key, read=read, write=write, delete=delete):
                return False
        return True

    def keys_json(self):
        keys = []
        for ds in DataSet.all().filter('account =', self.account).filter('name IN', self.names):
            keys.append(ds.encode())
        return simplejson.dumps(keys)
