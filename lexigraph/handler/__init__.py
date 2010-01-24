from functools import wraps
import logging

from google.appengine.api import users

from vendor.jinja2 import Environment, FileSystemLoader

from google.appengine.ext.webapp import RequestHandler as _RequestHandler
from lexigraph.log import ClassLogger
from lexigraph import model
from lexigraph.model.query import *
from lexigraph import config

class ErrorSignal(Exception):
    pass

class RedirectError(Exception):
    pass

class PermissionsError(Exception):
    pass

def requires_login(func):
    logger = logging.getLogger('lexigraph.handler')
    @wraps(func)
    def requires_login_inner(self):
        if self.user is None:
            logger.info('URI for %s requires login, redirecting' % (self,))
            self.redirect(users.create_login_url(self.request.uri))
        else:
            return func(self)
    return requires_login_inner

def cache_per_request(func):
    @wraps(func)
    def cache_per_request_inner(self, *args):
        if not hasattr(self.request, '_request_cache'):
            self.request._request_cache = {}
        cache_dict = self.request._request_cache
        cache_key = '%s.%s.%s' % (self.__class__.__name__, func.__name__, args)
        if cache_key not in cache_dict:
            cache_dict[cache_key] = func(self, *args)
        return cache_dict[cache_key]
    return cache_per_request_inner

class RequestHandler(_RequestHandler):

    log = ClassLogger()
    jinja_env = Environment(loader=FileSystemLoader('templates'))

    def initialize(self, request, response):
        super(RequestHandler, self).initialize(request, response)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        self.key = request.get('key') or None
        self.initialize_env()

    def initialize_env(self):
        self.env = {'config': config}

    def form_required(self, name, uri=None):
        """Get a thing in the form, redirecting if it is missing."""
        thing = self.request.get(name)
        if not thing:
            self.log.warning('form was missing field %s' % (name,))
            self.session['message'] = 'Form was missing field %s' % (name,)
            self.log.warning('uir = %r' % (uri,))
            self.redirect(uri or getattr(self, 'error_uri', self.request.uri))
        else:
            return thing


    def redirect(self, url, permanent=False):
        """Overriden to redirect RightNow using exceptions."""
        super(RequestHandler, self).redirect(url, permanent=permanent)
        raise RedirectError

    def handle_exception(self, exception, debug_mode):
        if isinstance(exception, RedirectError):
            pass
        else:
            return super(RequestHandler, self).handle_exception(exception, debug_mode)


def handle_error(func):
    @wraps(func)
    def closure(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ErrorSignal:
            pass
    return closure

from lexigraph.handler.interactive import *
