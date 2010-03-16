routing = []

def add_route(cls, uri_regex):
    routing.append((uri_regex, cls))

import lexigraph.view.account
import lexigraph.view.composite_dataset
import lexigraph.view.dashboard
import lexigraph.view.dataseries
import lexigraph.view.dataset
import lexigraph.view.groups
import lexigraph.view.home
import lexigraph.view.logout
import lexigraph.view.prefs
import lexigraph.view.cron
import lexigraph.view.tasks
import lexigraph.view.doc
import lexigraph.view.graph

import lexigraph.view.adhoc
import lexigraph.view.ajax
import lexigraph.view.api
import lexigraph.view.debug
