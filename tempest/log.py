import logging

LOG_PREFIX = 'tempest.'

def new_logger(name):
    return logging.getLogger(LOG_PREFIX + name)

class ClassLogger(object):
    """Courtesy bickfordb"""

    def __get__(self, obj, obj_type=None):
        object_class = obj_type or obj.__class__
        return new_logger(object_class.__module__ + '.' + object_class.__name__)
