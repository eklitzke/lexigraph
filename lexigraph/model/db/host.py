from google.appengine.ext import db

from lexigraph.model.db import LexigraphModel
from lexigraph.model import maybe_one

class Host(LexigraphModel):
    name = db.StringProperty(required=True)
    class_ = db.StringProperty()
