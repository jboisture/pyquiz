
from repoze.zodbconn.connector import CONNECTION_KEY

class TransferLog:
    """WSGI framework component that logs ZODB transfer stats to a file."""

    def __init__(self, next_app, logger, connection_key=CONNECTION_KEY):
        self.next_app = next_app
        self.logger = logger
        self.connection_key = connection_key

    def __call__(self, environ, start_response):
        conn = environ[self.connection_key]
        request_method = environ['REQUEST_METHOD']
        path_info = environ['PATH_INFO']
        query_string = environ.get('QUERY_STRING')
        loads_before, stores_before = conn.getTransferCounts()
        try:
            return self.next_app(environ, start_response)
        finally:
            loads_after, stores_after = conn.getTransferCounts()
            if query_string:
                url = '%s?%s' % (path_info, query_string)
            else:
                url = path_info
            loads = loads_after - loads_before
            stores = stores_after - stores_before
            self.logger.write('"%s","%s",%d,%d\n'
                                % (request_method, url, loads, stores))

def make_app(next_app, global_conf, **local_conf):
    """Make a TransferLog app.  Expects keyword parameters:

    class_regexes: a list of regular expressions matching class names
      to be kept in the cache.  Class names take the form
      "dotted_module_name:class_name".

    connection_key: Optional; the name of the key to get from the WSGI
        environment to retrieve the database connection.
    """
    filename = local_conf['filename']
    logger = open(filename, 'a', False)
    connection_key = local_conf.get('connection_key', CONNECTION_KEY)
    return TransferLog(next_app, logger, connection_key=connection_key)
