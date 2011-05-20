
from repoze.zodbconn.uri import db_from_uri

CONNECTION_KEY = 'repoze.zodbconn.connection'

class Connector:
    """WSGI framework component that opens and closes a ZODB connection.

    Downstream applications will have the connection in the environment,
    normally under the key 'repoze.zodbconn.connection'.
    """
    def __init__(self, next_app, db, connection_key=CONNECTION_KEY):
        self.next_app = next_app
        self.db = db
        self.connection_key = connection_key

    def __call__(self, environ, start_response):
        conn = self.db.open()
        environ[self.connection_key] = conn
        try:
            result = self.next_app(environ, start_response)
            return result
        finally:
            if self.connection_key in environ:
                del environ[self.connection_key]
            conn.transaction_manager.abort()
            conn.close()

def make_app(next_app, global_conf, **local_conf):
    """Make a Connector app.  Expects keyword parameters:

    zodb_uri: The database URI or URIs (either a whitespace-delimited string
      or a list of strings).  Can be in the global configuration.

    connection_key: Optional; the name of the key to put in the WSGI
        environment containing the database connection.
    """
    uri = local_conf.get('zodb_uri')
    if uri is None:
        uri = global_conf.get('zodb_uri')
    connection_key = local_conf.get('connection_key', CONNECTION_KEY)
    db = db_from_uri(uri)
    return Connector(next_app, db, connection_key=connection_key)
