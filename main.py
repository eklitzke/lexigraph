# fix up the environment before anything else
from lexigraph import gae_tweaks

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import lexigraph.view

application = webapp.WSGIApplication(lexigraph.view.routing, debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
  main()
