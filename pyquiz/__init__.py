from pkg_resources import resource_filename
from pyramid.config import Configurator
from pyramid.i18n import get_localizer
from pyramid.threadlocal import get_current_request
from repoze.zodbconn.finder import PersistentApplicationFinder
import deform

from pyquiz.resources import appmaker


def translator(term):
    return get_localizer(get_current_request()).translate(term)


class NonPersistentApplicationFinder(PersistentApplicationFinder):

    def __call__(self, environ):
        app = self.appmaker({})
        return app


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    zodb_uri = settings.get('zodb_uri')
    if zodb_uri is None:
        finder_class = NonPersistentApplicationFinder
    else:
        finder_class = PersistentApplicationFinder
    finder = finder_class(zodb_uri, appmaker)
    def get_root(request):
        return finder(request.environ)
    deform_template_dir = resource_filename('deform', 'templates/')
    deform.Form.set_zpt_renderer(deform_template_dir, translator=translator)
    config = Configurator(root_factory=get_root, settings=settings)
    config.add_static_view('static', 'pyquiz:static')
    config.add_static_view('static_deform', 'deform:static')
    config.add_translation_dirs('pyquiz:locale', 'colander:locale', 'deform:locale')
    config.scan('pyquiz')
    return config.make_wsgi_app()
