

import unittest

from persistent.mapping import PersistentMapping
class KeepMe(PersistentMapping):
    pass


class TestCacheCleanup(unittest.TestCase):
    def setUp(self):
        from ZODB.DB import DB
        from ZODB.MappingStorage import MappingStorage
        import transaction

        storage = MappingStorage()
        self.db = DB(storage)
        conn = self.db.open()
        root = conn.root()
        root['keepme'] = KeepMe()
        root['keepme']['extra'] = PersistentMapping()
        transaction.commit()
        conn.close()
        conn._resetCache()

    def tearDown(self):
        self.db.close()

    def test_cleanup(self):
        from repoze.zodbconn.cachecleanup import CacheCleanup
        connection_key = 'connection'

        def myapp(environ, start_response):
            conn = environ[connection_key]
            root = conn.root()
            root['keepme']['extra'].values()  # load objects
            self.assertNotEqual(conn._opened, None)
            self.assertEqual(root._p_changed, False)
            self.assertEqual(root['keepme']._p_changed, False)
            self.assertEqual(root['keepme']['extra']._p_changed, False)

        regexes = 'repoze.zodbconn.tests.test_cachecleanup:KeepMe'
        cleaner = CacheCleanup(myapp, regexes, connection_key=connection_key)

        # run this test twice to test class caching
        for i in range(2):
            conn = self.db.open()
            root = conn.root()
            environ = {connection_key: conn}
            cleaner(environ, None)
            self.assertEqual(root._p_changed, False)
            self.assertEqual(root['keepme']._p_changed, False)
            self.assertEqual(root['keepme']['extra']._p_changed, None)


class TestMakeApp(unittest.TestCase):
    def _callFUT(self, next_app, global_conf, **local_conf):
        from repoze.zodbconn.cachecleanup import make_app
        return make_app(next_app, global_conf, **local_conf)

    def test_default(self):
        def dummy_app(): pass
        app = self._callFUT(dummy_app, {}, class_regexes='repoze zope',
            connection_key='altkey')
        self.assertEqual(app.next_app, dummy_app)
        self.assertEqual(len(app.class_regexes), 2)
        self.assertEqual(app.connection_key, 'altkey')
