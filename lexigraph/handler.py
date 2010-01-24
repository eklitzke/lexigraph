from functools import wraps
import logging
import datetime

from google.appengine.api import users

from vendor.jinja2 import Environment, FileSystemLoader

from google.appengine.ext.webapp import RequestHandler as _RequestHandler
from lexigraph.log import ClassLogger
from lexigraph import model
import lexigraph.session
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
        self.env = {'title': ''}

        self.user = users.get_current_user()
        self.user_id = self.user.user_id() if self.user else None
        self.key = request.get('key') or None
        self.initialize_env()

    def initialize_env(self):
        self.session = None
        self.accounts = []
        if self.user:
            self.session = lexigraph.session.SessionState(self.user)
            self.accounts = model.Account.by_user(self.user)
        self.env['accounts'] = self.accounts
        self.env['session'] = self.session
        if self.user:
            self.env['account'] = self.account
        self.env['config'] = config

        # set the copyright date on the footers
        self.env['copyright_year'] = datetime.date.today().year

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

    @cache_per_request
    def get_dataset(self, name, check_read=True, check_write=False, check_delete=False):
        assert name
        ds = maybe_one(model.DataSet.all().filter('name =', name).filter('account =', self.account))
        if ds is not None and not ds.is_allowed(self.user, self.key, read=check_read, write=check_write, delete=check_delete):
            raise PermissionsError
        return ds

    def load_prefs(self):
        """Load preferences for the current user. No work is done if this method
        has already been called during this request.
        """
        if 'prefs' not in self.env:
            self.env['prefs'] = model.UserPrefs.load_by_user_id(self.user_id)
        return self.env['prefs']

    def redirect(self, url, permanent=False):
        """Overriden to redirect RightNow using exceptions."""
        super(RequestHandler, self).redirect(url, permanent=permanent)
        raise RedirectError

    def handle_exception(self, exception, debug_mode):
        if isinstance(exception, RedirectError):
            pass
        else:
            return super(RequestHandler, self).handle_exception(exception, debug_mode)

    @property
    def account(self):
        #import traceback
        #self.log.info('tb = %s' % (traceback.format_stack(),))
        if not (self.user or self.key):
            return None
        if self.key:
            group = maybe_one(model.AccessGroup.all().filter('api_token =', self.key))
            if not group:
                self.log.info('No AccessGroup associated with key %s' % (self.key,))
                return None
            return group.account

        account = self.session['account']
        if account is None:
            accounts = model.Account.by_user(self.user)
            if not accounts:
                self.session['message'] = 'You must create an account first.'
                account = None
            elif len(accounts) == 1:
                account = accounts[0]
                self.session['account'] = account
            else:
                self.session['message'] = 'Select an account.'
                #self.redirect('/choose/account')
                account = None
        else:
            self.log.info('hit account = %s in session' % (account,))
        return account

    def get_template(self, name):
        return self.jinja_env.get_template(name)

    def render_template(self, name):
        template = self.get_template(name)
        self.response.out.write(template.render(**self.env))

    #def error(self, code):
    #    super(RequestHandler, self).error(code)
    #    raise ErrorSignal

def handle_error(func):
    @wraps(func)
    def closure(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ErrorSignal:
            pass
    return closure
