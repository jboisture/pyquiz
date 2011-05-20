import unittest


class TestEnvironmentDeleterMiddleware(unittest.TestCase):
    def _getTargetClass(self):
        from repoze.zodbconn.middleware import EnvironmentDeleterMiddleware
        return EnvironmentDeleterMiddleware

    def _makeOne(self, *arg, **kw):
        return self._getTargetClass()(*arg, **kw)

    def test_default_key(self):
        from repoze.zodbconn.middleware import CLOSER_KEY
        app = DummyApplication()
        mw = self._makeOne(app)
        environ = {CLOSER_KEY:'123'}
        mw(environ, None)
        self.failIf(CLOSER_KEY in environ)
        
    def test_nondefault_key(self):
        app = DummyApplication()
        mw = self._makeOne(app, 'abc')
        environ = {'abc':'123'}
        mw(environ, None)
        self.failIf('abc' in environ)

    def test_exception_when_app_called(self):
        app = DummyRaisingApplication()
        mw = self._makeOne(app, 'abc')
        environ = {'abc':'123'}
        self.assertRaises(KeyError, mw, environ, None)
        self.failIf('abc' in environ)


class TestMakeMiddleware(unittest.TestCase):
    def _callFUT(self, *arg, **kw):
        from repoze.zodbconn.middleware import make_middleware
        return make_middleware(*arg, **kw)

    def test_it(self):
        app = DummyApplication()
        global_conf = {}
        local_conf = {'key':'abc'}
        mw = self._callFUT(app, global_conf, **local_conf)
        self.assertEqual(mw.application, app)
        self.assertEqual(mw.key, 'abc')
        
class DummyApplication:
    called = False
    def __call__(self, environ, start_response):
        self.called = True

class DummyRaisingApplication:
    def __call__(self, environ, start_response):
        raise KeyError('foo')
    
