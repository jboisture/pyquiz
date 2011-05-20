import unittest

class TestConnector(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.zodbconn.connector import Connector
        return Connector

    def _makeOne(self, next_app, db, **kwargs):
        klass = self._getTargetClass()
        return klass(next_app, db, **kwargs)

    def test_ctor(self):
        def dummy_app(): pass
        db = DummyDB()
        app = self._makeOne(dummy_app, db, connection_key='altkey')
        self.assertEqual(app.next_app, dummy_app)
        self.assertEqual(app.db, db)
        self.assertEqual(app.connection_key, 'altkey')

    def test_call(self):
        from repoze.zodbconn.connector import CONNECTION_KEY
        def dummy_app(environ, start_response):
            conn = environ[CONNECTION_KEY]
            return conn
        db = DummyDB()
        app = self._makeOne(dummy_app, db)
        environ = {}
        conn = app(environ, None)
        self.assertEqual(conn.closed, True)
        self.assertFalse(CONNECTION_KEY in environ)

    def test_app_deletes_connection(self):
        from repoze.zodbconn.connector import CONNECTION_KEY
        def dummy_app(environ, start_response):
            conn = environ[CONNECTION_KEY]
            del environ[CONNECTION_KEY]
            return conn
        db = DummyDB()
        app = self._makeOne(dummy_app, db)
        environ = {}
        conn = app(environ, None)
        self.assertEqual(conn.closed, True)
        self.assertFalse(CONNECTION_KEY in environ)

    def test_close_on_exception(self):
        # close the connection even when an exception occurs
        from repoze.zodbconn.connector import CONNECTION_KEY
        def dummy_app(environ, start_response):
            conn = environ[CONNECTION_KEY]
            environ['testconn'] = conn
            raise ValueError('synthetic exception')
        db = DummyDB()
        app = self._makeOne(dummy_app, db)
        environ = {}
        self.assertRaises(ValueError, app, environ, None)
        conn = environ['testconn']
        self.assertEqual(conn.closed, True)
        self.assertFalse(CONNECTION_KEY in environ)


class TestMakeApp(unittest.TestCase):
    def setUp(self):
        from repoze.zodbconn.resolvers import RESOLVERS
        self.db = DummyDB()
        def dbfactory():
            return self.db
        RESOLVERS['foo'] = lambda *arg: ('key', 'arg', 'kw', dbfactory)

    def tearDown(self):
        from repoze.zodbconn.resolvers import RESOLVERS
        del RESOLVERS['foo']

    def _callFUT(self, next_app, global_conf, **local_conf):
        from repoze.zodbconn.connector import make_app
        return make_app(next_app, global_conf, **local_conf)

    def test_default(self):
        def dummy_app(): pass
        app = self._callFUT(dummy_app, {}, zodb_uri='foo://',
            connection_key='altkey')
        self.assertEqual(app.next_app, dummy_app)
        self.assertEqual(app.db, self.db)
        self.assertEqual(app.connection_key, 'altkey')

    def test_global_conf(self):
        def dummy_app(): pass
        app = self._callFUT(dummy_app, {'zodb_uri': 'foo://'},
            connection_key='altkey')
        self.assertEqual(app.next_app, dummy_app)
        self.assertEqual(app.db, self.db)
        self.assertEqual(app.connection_key, 'altkey')

class DummyDB:
    def __init__(self):
        self.databases = {'unnamed': self}
    def open(self):
        return DummyConnection()

class DummyTransactionManager:
    def abort(self):
        pass

class DummyConnection:
    closed = False

    def close(self):
        self.closed = True

    transaction_manager = DummyTransactionManager()
