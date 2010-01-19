routing = []
    # [(r'/', Home),
    #  (r'/dashboard', Dashboard),
    #  (r'/new_account', NewAccout),
    #  (r'/cron/trim', cron.DataPointTrim),
    #  (r'/api/csv', api.CSV),
    #  (r'/api/insert', api.Insert),
    #  (r'/api/schema', api.Schema),
    #  (r'/api/create/dataset', api.CreateDataSet),
    #  (r'/api/create/series', api.CreateSeriesSchema),
    #  (r'/api/create/point', api.CreatePoint),
    #  (r'/.*', Home) # fall-through case is to go to home, which redirects to /


def add_route(cls, uri_regex):
    routing.append((uri_regex, cls))

from lexigraph.view.home import Home
import lexigraph.view.account
import lexigraph.view.dataset
import lexigraph.view.groups
import lexigraph.view.logout
import lexigraph.view.prefs
import lexigraph.view.cron.trim_sessions

from lexigraph.view.new_dataseries import NewDataSeries
from lexigraph.view.new_datapoint import NewDataPoint
from lexigraph.view.dashboard import Dashboard

from lexigraph.view import api
