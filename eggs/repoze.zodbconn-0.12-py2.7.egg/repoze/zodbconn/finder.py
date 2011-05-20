
from repoze.zodbconn.uri import db_from_uri
from repoze.zodbconn.uri import dbfactory_from_uri  # BBB
from repoze.zodbconn.connector import CONNECTION_KEY

class SimpleCleanup:
    def __init__(self, conn, environ):
        # N.B.:  do *not* create a cycle by holding on to 'environ'!
        self.cleaner = conn.close

    def __del__(self):
        self.cleaner()

class LoggingCleanup:
    logger = None

    def __init__(self, conn, environ):
        # N.B.:  do *not* create a cycle by holding on to 'environ'!
        self.conn = conn
        self.request_method = environ['REQUEST_METHOD']
        self.path_info = environ['PATH_INFO']
        self.query_string = environ.get('QUERY_STRING')
        self.loads_before, self.stores_before = conn.getTransferCounts()

    #############  WAAAAAAAAAAA!!!!!!########################################
    # For some insane reason, the coverage module thinks this entire method
    # is uncovered, in spite of the fact that the passing unit tests prove
    # that both code paths get executed.
    #########################################################################
    def __del__(self): #pragma NO COVERAGE
        loads_after, stores_after = self.conn.getTransferCounts()
        self.conn.close()
        if self.logger is not None:
            if self.query_string:
                url = '%s?%s' % (self.path_info, self.query_string)
            else:
                url = self.path_info
            loads = loads_after - self.loads_before
            stores = stores_after - self.stores_before
            self.logger.write('"%s","%s",%d,%d\n'
                                % (self.request_method, url, loads, stores))

class PersistentApplicationFinder:
    def __init__(self, uri, appmaker, cleanup=SimpleCleanup,
            connection_key=CONNECTION_KEY):
        self.uri = uri
        self.appmaker = appmaker
        self.connection_key = connection_key
        self.cleanup = cleanup
        if uri is None: # it will be None during *tests* only
            self.db = None
        else:
            self.db = db_from_uri(self.uri)

    def __call__(self, environ):
        conn = None

        if self.connection_key:
            conn = environ.get(self.connection_key)

        if conn is None:
            conn = self.db.open()
            # We opened this connection, which means we have the
            # responsibility for closing it.
            environ['repoze.zodbconn.closer'] = self.cleanup(conn, environ)

        root = conn.root()
        app = self.appmaker(root)

        return app
