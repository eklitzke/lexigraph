import re

from lexigraph.view import add_route
from lexigraph.handler import SessionHandler
from lexigraph import model
from lexigraph.cache import CacheDict
from lexigraph.model.query import *

digit_re = re.compile(r'^\d+')
nondigit_re = re.compile(r'^\D+')

def name_to_value(name):
    """Try to sort things like load1 and load10 in the right order."""
    parts = []
    for part in name.split('-'):
        if not part:
            continue
        p = part
        while p:
            m = digit_re.match(p)
            if m:
                num = m.group()
                p = p[len(num):]
                parts.append(int(num))
                continue
            m = nondigit_re.match(part)
            if m:
                string = m.group()
                p = p[len(string):]
                parts.append(string)
                continue
            break
    return tuple(parts)

class TagQueryCache(CacheDict):

    def normalize_key(self, (account, user, tag_list)):
        return (account.key().id(), user.user_id(), sorted(tag_list))

    def select_by_tags(self, account, user, tag_list):
        """Return datasets containing all tags in the list."""
        # XXX: for now, we only now how to cache queries for exactly one tag
        #(because that's the only way that I know how to make remove_by_tags
        #correct).
        use_memcache = False
        val = None
        if len(tag_list) <= 1:
            val = self[(account, user, tag_list)]
            use_memcache = True
        val = use_memcache = None # FIXME
        if val is None:
            q = model.DataSet.all().filter('account =', account)
            for tag in tag_list:
                q = q.filter('tags =', tag)
            val = [ds.name for ds in fetch_all(q) if ds.is_allowed(user, read=True)]
            val.sort(key=name_to_value)
            if use_memcache:
                self[(account, user, tag_list)] = val
        return val

    def remove_by_tags(self, account, tags):
        raise NotImplementedError

class RenderGraph(SessionHandler):

    requires_login = True

    def get(self):
        tags = [x.strip() for x in self.request.get('tags').split(',')]
        self.env['names'] = names = TagQueryCache().select_by_tags(self.account, self.user, tags)
        self.render_ajax('ajax/graphs.html', extra={'names': names})
        
add_route(RenderGraph, '/ajax/graphs')
