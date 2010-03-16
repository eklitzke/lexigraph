import datetime

from lexigraph.view import add_route
from lexigraph import model
from lexigraph.handler import InteractiveHandler

from lexigraph.view.cron import CronRequestHandler

class FixAccounts(CronRequestHandler):
    """Add a display_name to accounts without one."""

    def get(self):
        for account in model.Account.all():
            if not getattr(account, 'display_name', None):
                account.display_name = account.name
                account.put()
            if not getattr(account, 'last_login', None):
                account.last_login = datetime.datetime(2000, 1, 1)
                account.put()

add_route(FixAccounts, '/adhoc/fixaccounts')
