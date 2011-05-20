import unittest

class TestSimpleCleanup(unittest.TestCase):

    def _getTargetClass(self):
        from repoze.zodbconn.finder import SimpleCleanup
        return SimpleCleanup

    def _makeOne(self, cleaner, environ):
        return self._getTargetClass()(cleaner, environ)

    def test___del___calls_cleaner(self):
        root = DummyRoot()
        conn = DummyConn(root)
        environ = {}
        cleanup = self._makeOne(conn, environ)
        del cleanup
        self.failUnless(root.closed)

class TestLoggingCleanup(unittest.TestCase):

    def _getTargetClass(self):
        from repoze.zodbconn.finder import LoggingCleanup
        return LoggingCleanup

    def _makeOne(self, cleaner, environ):
        return self._getTargetClass()(cleaner, environ)

    def test___del___calls_cleaner_and_logs_no_qs(self):
        logger = DummyLogger()
        root = DummyRoot()
        conn = DummyConn(root)
        environ = {'REQUEST_METHOD': 'GET',
                   'PATH_INFO': '/test',
                  }
        cleanup = self._makeOne(conn, environ)
        cleanup.logger = logger
        del cleanup
        self.failUnless(root.closed)
        self.assertEqual(len(logger._wrote), 1)
        self.assertEqual(logger._wrote[0], '"GET","/test",0,0\n')

    def test___del___calls_cleaner_and_logs_w_qs(self):
        logger = DummyLogger()
        root = DummyRoot()
        conn = DummyConn(root)
        environ = {'REQUEST_METHOD': 'GET',
                   'PATH_INFO': '/test',
                   'QUERY_STRING': 'foo=bar',
                  }
        cleanup = self._makeOne(conn, environ)
        cleanup.logger = logger
        del cleanup
        self.failUnless(root.closed)
        self.assertEqual(len(logger._wrote), 1)
        self.assertEqual(logger._wrote[0], '"GET","/test?foo=bar",0,0\n')

_marker = object()

class TestPersistentApplicationFinder(unittest.TestCase):
    def setUp(self):
        from repoze.zodbconn.resolvers import RESOLVERS
        self.root = DummyRoot()
        self.db = DummyDB(self.root, 'foo')
        def dbfactory():
            return self.db
        RESOLVERS['foo'] = lambda *arg: ('key', 'arg', 'kw', dbfactory)

    def tearDown(self):
        from repoze.zodbconn.resolvers import RESOLVERS
        del RESOLVERS['foo']

    def _getTargetClass(self):
        from repoze.zodbconn.finder import PersistentApplicationFinder
        return PersistentApplicationFinder

    def _makeOne(self, uri, appmaker, **kw):
        klass = self._getTargetClass()
        return klass(uri, appmaker, **kw)

    def test_ctor(self):
        from repoze.zodbconn.finder import SimpleCleanup
        def makeapp(root): pass
        finder = self._makeOne('foo://bar.baz', makeapp)
        self.assertEqual(finder.uri, 'foo://bar.baz')
        self.assertEqual(finder.appmaker, makeapp)
        self.failUnless(finder.cleanup is SimpleCleanup)

    def test_call_no_db_no_cleanup(self):
        def makeapp(root):
            root.made = True
            return 'abc'
        finder = self._makeOne('foo://bar.baz', makeapp)
        environ = {}
        app = finder(environ)
        self.assertEqual(app, 'abc')
        self.assertEqual(self.root.made, True)
        self.assertEqual(self.root.closed, False)
        del environ['repoze.zodbconn.closer']
        self.assertEqual(self.root.closed, True)
        self.assertEqual(finder.db, self.db)

    def test_call_no_db_w_cleanup(self):
        def makeapp(root):
            root.made = True
            return 'abc'
        finder = self._makeOne('foo://bar.baz', makeapp, cleanup=DummyCleanup)
        environ = {}
        app = finder(environ)
        self.assertEqual(app, 'abc')
        self.assertEqual(self.root.made, True)
        self.assertEqual(self.root.closed, False)
        self.assertEqual(environ['XXX'], None)
        del environ['repoze.zodbconn.closer']
        self.assertEqual(self.root.closed, True)
        self.assertEqual(finder.db, self.db)

    def test_call_with_db_no_cleanup(self):
        def makeapp(root):
            root.made = True
            return 'abc'
        finder = self._makeOne(None, makeapp)
        finder.db = DummyDB(self.root, 'another')
        environ = {}
        app = finder(environ)
        self.assertEqual(app, 'abc')
        self.assertEqual(self.root.made, True)
        self.assertEqual(self.root.closed, False)
        del environ['repoze.zodbconn.closer']
        self.assertEqual(self.root.closed, True)

    def test_call_with_db_w_cleanup(self):
        def makeapp(root):
            root.made = True
            return 'abc'
        finder = self._makeOne(None, makeapp, cleanup=DummyCleanup)
        finder.db = DummyDB(self.root, 'another')
        environ = {}
        app = finder(environ)
        self.assertEqual(app, 'abc')
        self.assertEqual(self.root.made, True)
        self.assertEqual(self.root.closed, False)
        self.assertEqual(environ['XXX'], None)
        del environ['repoze.zodbconn.closer']
        self.assertEqual(self.root.closed, True)

    def test_get_connection_from_environ(self):
        def makeapp(root):
            root.made = True
            return 'abc'
        finder = self._makeOne('foo://bar.baz', makeapp)
        db = DummyDB(self.root, 'another')
        conn = db.open()
        environ = {'repoze.zodbconn.connection': conn}
        app = finder(environ)
        self.assertEqual(app, 'abc')
        self.assertEqual(self.root.made, True)
        self.assertEqual(self.root.closed, False)
        self.assertFalse('repoze.zodbconn.closer' in environ)

    def test_ignore_connection_from_environ(self):
        def makeapp(root):
            root.made = True
            return 'abc'
        finder = self._makeOne('foo://bar.baz', makeapp, connection_key=None)
        db = DummyDB(self.root, 'another')
        conn = db.open()
        environ = {'repoze.zodbconn.connection': conn}
        app = finder(environ)
        self.assertEqual(app, 'abc')
        self.assertEqual(self.root.made, True)
        self.assertEqual(self.root.closed, False)
        self.assertTrue('repoze.zodbconn.closer' in environ)

    def test_call_no_uri(self):
        def makeapp(root):
            root.made = True
            return 'abc'
        finder = self._makeOne('', makeapp)
        db = DummyDB(self.root, 'another')
        conn = db.open()
        environ = {'repoze.zodbconn.connection': conn}
        app = finder(environ)
        self.assertEqual(app, 'abc')
        self.assertEqual(self.root.made, True)
        self.assertEqual(self.root.closed, False)
        self.assertFalse('repoze.zodbconn.closer' in environ)


class DummyRoot:
    closed = False

class DummyConn:
    closed = False
    _loads = _saves = 0

    def __init__(self, rootob):
        self.rootob = rootob

    def root(self):
        return self.rootob

    def close(self):
        self.rootob.closed = True

    def getTransferCounts(self):
        return self._loads, self._saves

class DummyCleanup:
    def __init__(self, conn, environ):
        self.conn = conn
        environ['XXX'] = None
    def __del__(self):
        self.conn.close()

class DummyDB:
    def __init__(self, rootob, database_name):
        self.conn = DummyConn(rootob)
        self.database_name = database_name
        self.databases = {database_name: self}

    def open(self):
        return self.conn

class DummyLogger:
    def __init__(self):
        self._wrote = []

    def write(self, chunk):
        self._wrote.append(chunk)
