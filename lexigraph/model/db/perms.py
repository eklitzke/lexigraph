from functools import wraps

from google.appengine.ext import db

from lexigraph.cache import surrogate_key, CacheDict
from lexigraph.model.db import APIError, LexigraphModel
