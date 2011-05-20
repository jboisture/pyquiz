
import re
from ZODB.utils import z64
from repoze.zodbconn.connector import CONNECTION_KEY

class CacheCleanup:
    """WGSI framework component that reduces the ZODB cache.

    Keeps only objects of certain classes.
    """

    def __init__(self, next_app, class_regexes, connection_key=CONNECTION_KEY):
        self.next_app = next_app
        self.connection_key = connection_key
        if isinstance(class_regexes, basestring):
            class_regexes = [re.compile(expr) for expr in class_regexes.split()]
        self.class_regexes = class_regexes
        self._class_cache = {}  # {class -> keep (boolean)}

    def __call__(self, environ, start_response):
        conn = environ[self.connection_key]
        if not hasattr(conn, '_loaded_oids'):
            patch_connection(conn)
        try:
            return self.next_app(environ, start_response)
        finally:
            self.cleanup(conn)

    def cleanup(self, conn):
        class_cache = self._class_cache
        class_cache_get = class_cache.get
        for oid in conn._loaded_oids:
            if oid == z64:
                continue
            obj = conn.get(oid)
            if obj._p_changed is not None:
                klass = obj.__class__
                keep = class_cache_get(klass)
                if keep is None:
                    keep = self.keep_class(klass)
                    class_cache[klass] = keep
                if not keep:
                    # ghostify the object
                    obj._p_changed = None
        conn._loaded_oids.clear()

    def keep_class(self, klass):
        name = '%s:%s' % (klass.__module__, klass.__name__)
        for expr in self.class_regexes:
            if expr.match(name) is not None:
                return True
        return False


def patch_connection(conn):
    """Add the object load tracking feature to a ZODB connection."""
    conn._loaded_oids = set()
    real_setstate = conn.setstate
    def setstate(obj):
        real_setstate(obj)
        conn._loaded_oids.add(obj._p_oid)
    conn.setstate = setstate


def make_app(next_app, global_conf, **local_conf):
    """Make a CacheCleanup app.  Expects keyword parameters:

    class_regexes: a list of regular expressions matching class names
      to be kept in the cache.  Class names take the form
      "dotted_module_name:class_name".

    connection_key: Optional; the name of the key to get from the WSGI
        environment to retrieve the database connection.
    """
    class_regexes = local_conf['class_regexes']
    connection_key = local_conf.get('connection_key', CONNECTION_KEY)
    return CacheCleanup(next_app, class_regexes, connection_key=connection_key)
