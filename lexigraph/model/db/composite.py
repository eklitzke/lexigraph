from lexigraph.model.db import LexigraphModel, Account
from google.appengine.ext import db
from lexigraph.model.db import DataSet
from django.utils import simplejson
from lexigraph import crypt

# TODO add permissions
class CompositeDataSet(LexigraphModel):
    name = db.StringProperty(required=True)
    datasets = db.ListProperty(int, required=True)
    hostname = db.StringProperty()
    tags = db.StringListProperty()
    scale = db.FloatProperty()
    account = db.ReferenceProperty(Account, required=True)

    @classmethod
    def create(cls, name, names, account, hostname, tags):
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
        for dataset in self.datasets:
            dataset = DataSet.get_by_id(dataset)
            self.log.info('name = %s, key = %s' % (dataset.name, dataset.encode()))
            if not dataset.is_allowed(user=user, api_key=api_key, read=read, write=write, delete=delete):
                return False
        return True

    def keys_json(self):
        return simplejson.dumps([crypt.encode(id) for id in self.datasets])
