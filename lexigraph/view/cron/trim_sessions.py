from lexigraph.view import add_route
from lexigraph.view.cron._common import *
from lexigraph.session import SessionStorage

class TrimSessions(CronRequestHandler):

    def get(self):
        rowcount = SessionStorage.remove_expired()
        self.response.out.write('Trimmed %d rows' % (rowcount,))

add_route(TrimSessions, '/cron/trim/sessions')
