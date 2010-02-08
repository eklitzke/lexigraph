import string

# Arbitrary characters that I think are OK. None of these should require 
# escaping, either
VALID_CHARS = set(string.ascii_letters + string.digits + '_-():.')
error_msg = '%%r had characters outside of %s' % (''.join(sorted(VALID_CHARS)),)

class ValidationError(ValueError):
    pass

def is_name_valid(name):
    return all(c in VALID_CHARS for c in name)

def validate_name(name):
    if not is_name_valid(name):
        raise ValueError(error_msg % (name,))
