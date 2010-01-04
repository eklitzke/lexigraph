# fix up the environment before anything else
from tempest import gae_tweaks

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from tempest.view import *

application = webapp.WSGIApplication(
    [(r'/', Home),
     (r'/api/csv', api.CSV),
     (r'/api/insert', api.Insert),
     (r'/api/schema', api.Schema),
     (r'/api/create/dataset', api.CreateDataSet),
     (r'/api/create/series', api.CreateSeriesSchema),
     (r'/api/create/point', api.CreatePoint),
     (r'/.*', Home) # fall-through case is to go to home, which redirects to /
    ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
