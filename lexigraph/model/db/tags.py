from google.appengine.ext import db

from lexigraph.model.query import maybe_one, fetch_all
from lexigraph.model.db import LexigraphModel

class TagColors(LexigraphModel):
    name = db.StringProperty(required=True)
    owner = db.UserProperty(required=True)

    red = db.IntegerProperty(required=True)
    green = db.IntegerProperty(required=True)
    blue = db.IntegerProperty(required=True)
    alpha = db.FloatProperty(required=True)

    DEFAULT_GREY = 240

    @classmethod
    def colors_for_tags(cls, user, names):
        rows = fetch_all(cls.all().filter('owner =', user).filter('name IN', names))
        result = rows[:]
        cls.log.info('-----')
        cls.log.info('names = %s' % (names,))
        for name in set(names) - set(r.name for r in rows):
            cls.log.info('adding fake for %s' % name)
            row = cls(name=name, owner=user, red=cls.DEFAULT_GREY, blue=cls.DEFAULT_GREY, green=cls.DEFAULT_GREY, alpha=0.0)
            row.put()
            result.append(row)
        result.sort(key=lambda r: r.name)
        cls.log.info('result = %s' % (result,))
        cls.log.info('-----')
        return result

    @classmethod
    def update_color(cls, user, name, red, green, blue, alpha=0.0):
        row = maybe_one(cls.all().filter('user =', user).filter('name =', name))
        if row:
            row.red, row.green, row.blue, row.alpha = red, green, blue, alpha
        else:
            row = cls(owner=user, name=name, red=red, green=green, blue=blue, alpha=alpha)
        row.put()
