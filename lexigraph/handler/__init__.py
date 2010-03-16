from functools import wraps
import logging

import os
from google.appengine.api import users
from django.utils import simplejson

from vendor.jinja2 import Environment, FileSystemLoader

from google.appengine.ext.webapp import RequestHandler as _RequestHandler
from lexigraph.log import ClassLogger
from lexigraph import model
from lexigraph import config
from lexigraph.config import serials
from lexigraph.handler.errors import *
from lexigraph.validate import ValidationError


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
        self.uri = request.environ['PATH_INFO']
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        self.key = request.get('key') or None
        self.initialize_env()

    def initialize_env(self):
        self.env = {'config': config, 'serials': serials.hashes, 'use_ssl': True}
        if hasattr(config.level, 'is_live'):
            self.env['is_live'] = config.level.is_live
        else:
            self.env['is_live'] = not os.environ['SERVER_SOFTWARE'].startswith('Development')

    def form_required(self, name, uri=None, message=None):
        """Get a thing in the form, redirecting if it is missing."""
        thing = self.request.get(name)
        if not thing:
            if hasattr(self, 'session'):
                if not message:
                    message = 'Form was missing field %s' % (name,)
                self.log.warning('form was missing field %s; setting error_message = %r' % (name, message))
                self.session['error_message'] = message
            else:
                self.log.warning('form was missing field %s; no session provided' % (name,))
            self.redirect(uri or getattr(self, 'error_uri', self.request.uri))
        else:
            return thing

    def redirect(self, url, permanent=False):
        """Overriden to redirect RightNow using exceptions."""
        super(RequestHandler, self).redirect(url, permanent=permanent)
        raise RedirectError

    def get_template(self, name):
        return self.jinja_env.get_template(name)

    def render_ajax(self, template_name, code=0, extra={}):
        template = self.get_template(template_name)
        obj = {'text': template.render(**self.env), 'code': code}
        if extra:
            obj.update(extra)
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        self.response.out.write(simplejson.dumps(obj))

    def render_json(self, obj):
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        self.response.out.write(simplejson.dumps(obj))

    def handle_exception(self, exception, debug_mode):
        self.log.info('Handling exception %r (type is %s)' % (exception, type(exception)))
        if isinstance(exception, RedirectError):
            pass
        elif isinstance(exception, ValidationError):
            if getattr(self.session, None):
                self.session['error_message'] = str(exception)
            else:
                raise
        else:
            self.log.exception("uncaught exception")
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
from lexigraph.handler.tags import *
