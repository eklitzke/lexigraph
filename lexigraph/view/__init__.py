routing = []

def add_route(cls, uri_regex):
    routing.append((uri_regex, cls))

from lexigraph.view.home import Home
import lexigraph.view.account
import lexigraph.view.dataset
import lexigraph.view.groups
import lexigraph.view.logout
import lexigraph.view.prefs
import lexigraph.view.cron
import lexigraph.view.doc

from lexigraph.view.new_dataseries import NewDataSeries
from lexigraph.view.new_datapoint import NewDataPoint
from lexigraph.view.dashboard import Dashboard

from lexigraph.view import api
