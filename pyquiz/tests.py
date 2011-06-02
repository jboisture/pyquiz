import unittest

from pyramid import testing

class ViewTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()


    def test_view_create_test(self):
        from pyquiz.views import view_create_test
        request = testing.DummyRequest()
        info = view_create_test(request)
        import pdb
        pdb.set_trace()
        print self.assertEqual(info['project'], 'pyquiz')


class FunctionalTests(unittest.TestCase):
    
    def setUp(self):
        from pyquiz import main
        from webtest import TestApp
        app = main({})
        self.testapp = TestApp(app)

    def test_root(self):
        response = self.testapp.get('/', status=200)
        self.assertEquals(response.lxml.xpath('id("right")/h2/text()')[0], 'Pyramid links')

