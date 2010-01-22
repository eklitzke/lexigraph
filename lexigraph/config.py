# Configuration nonsense for lexigraph. Uses Yelp configuration conventions.

try:
    import lexigraph.level as level
except ImportError:
    level = object()

def mkvar(name, default):
    globals()[name] = getattr(level, name, default)

mkvar('whitelisted_emails', ['evan@eklitzke.org', 'test@example.com'])
