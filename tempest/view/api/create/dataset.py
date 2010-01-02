from tempest.view.api._common import *

class CreateDataSet(ApiRequestHandler):

    @encode_json
    def post(self):
        name = self.request.get('name')
        # ensure that the name is unique
        existing = DataSet.all().filter('name =', name).fetch(1)
        if existing:
            return {'status': StatusCodes.ALREADY_EXISTS}

        aggregate = self.request.get('aggregate')
        assert aggregate in ('min', 'max', 'sum', 'avg')

        # XXX: attributes are ignored, for the time being
        ds = DataSet(name=name, aggregate=AggregateType.from_string(aggregate))
        ds.put()

        return {'status': StatusCodes.OK, 'id': ds.key().id()}

__all__ = ['CreateDataSet']
