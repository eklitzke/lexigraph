import re
from lexigraph.handler.interactive import SessionHandler
from lexigraph import model
import lexigraph.log

logger = lexigraph.log.new_logger('handler.tags')

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

class TagsMixin(SessionHandler):

    def datasets_by_tags(self, tags_list):
        # composite datasets always come first
        q = model.CompositeDataSet.all().filter('account =', self.account)
        for tag in tags_list:
            q = q.filter('tags =', tag)
        # TODO: add is_allowed
        val = list(q)

        q = model.DataSet.all().filter('account =', self.account)
        for tag in tags_list:
            q = q.filter('tags =', tag)
        remaining = [ds for ds in q if ds.is_allowed(self.user, read=True)]
        remaining.sort(key=lambda x: name_to_value(x.name))
        val.extend(remaining)
        logger.info("val = %s " % (val,))
        return val
