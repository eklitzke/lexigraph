from tempest.view.api._common import *

class CreateSeriesSchema(ApiRequestHandler):

    @encode_json
    def post(self):
        data_set = self.request.get('data_set')
        interval = int(self.request.get('interval'), 10)
        max_age = self.request.get('max_age')
        max_age = int(max_age) if max_age else None

        ds, = DataSet.all().filter('name =', data_set).fetch(1)
        # ensure that the tuple (ds, inteval) is unique
        existing = SeriesSchema.all().filter('data_set =', ds).filter('interval =', interval).fetch(1)
        if existing:
            return {'status': StatusCodes.ALREADY_EXISTS}

        series = SeriesSchema(data_set=ds, interval=interval)#, max_age=max_age)
        series.put()
        return {'status': StatusCodes.OK, 'id': series.key().id()}

__all__ = ['CreateSeriesSchema']
