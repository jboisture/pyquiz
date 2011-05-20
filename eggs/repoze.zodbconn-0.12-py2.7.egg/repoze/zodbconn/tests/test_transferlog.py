
import unittest

class TestTransferLog(unittest.TestCase):

    def _getTargetClass(self):
        from repoze.zodbconn.transferlog import TransferLog
        return TransferLog

    def _makeOne(self, next_app, logger, **kw):
        return self._getTargetClass()(next_app, logger, **kw)

    def test_without_query_string(self):
        logger = DummyLogger()
        conn = DummyConn()
        environ = {'REQUEST_METHOD': 'GET',
                   'PATH_INFO': '/test',
                   'repoze.zodbconn.connection': conn,
                  }
        def myapp(environ, start_response):
            environ['repoze.zodbconn.connection'].fake_transfer()
        app = self._makeOne(myapp, logger)
        app(environ, None)
        self.assertEqual(len(logger._wrote), 1)
        self.assertEqual(logger._wrote[0], '"GET","/test",2,1\n')

    def test_with_query_string(self):
        logger = DummyLogger()
        conn = DummyConn()
        environ = {'REQUEST_METHOD': 'GET',
                   'PATH_INFO': '/test',
                   'repoze.zodbconn.connection': conn,
                   'QUERY_STRING': 'foo=bar',
                  }
        def myapp(environ, start_response):
            environ['repoze.zodbconn.connection'].fake_transfer()
        app = self._makeOne(myapp, logger)
        app(environ, None)
        self.assertEqual(len(logger._wrote), 1)
        self.assertEqual(logger._wrote[0], '"GET","/test?foo=bar",2,1\n')


class TestMakeApp(unittest.TestCase):
    def _callFUT(self, next_app, global_conf, **local_conf):
        from repoze.zodbconn.transferlog import make_app
        return make_app(next_app, global_conf, **local_conf)

    def test_it(self):
        def dummy_app(): pass
        import tempfile
        f = tempfile.NamedTemporaryFile()
        app = self._callFUT(dummy_app, {}, filename=f.name,
            connection_key='altkey')
        self.assertEqual(app.next_app, dummy_app)
        self.assertEqual(app.logger.name, f.name)
        self.assertEqual(app.connection_key, 'altkey')
        f.close()


class DummyLogger:
    def __init__(self):
        self._wrote = []

    def write(self, chunk):
        self._wrote.append(chunk)

class DummyConn:
    _loads = _saves = 0

    def fake_transfer(self):
        self._loads += 2
        self._saves += 1

    def getTransferCounts(self):
        return self._loads, self._saves

