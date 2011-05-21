from pkg_resources import resource_filename
from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from sqlalchemy.pool import NullPool

from pyquiz.models import initialize_sql


from pyramid.i18n import get_localizer
from pyramid.threadlocal import get_current_request

import deform



def translator(term):
    return get_localizer(get_current_request()).translate(term)

"""
class NonPersistentApplicationFinder(PersistentApplicationFinder):

    def __call__(self, environ):
        app = self.appmaker({})
        return app"""


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    """zodb_uri = settings.get('zodb_uri')
    if zodb_uri is None:
        finder_class = NonPersistentApplicationFinder
    else:
        finder_class = PersistentApplicationFinder
    finder = finder_class(zodb_uri, appmaker)
    def get_root(request):
        return finder(request.environ)"""
    engine = engine_from_config(settings, 'sqlalchemy.',poolclass=NullPool)
    initialize_sql(engine)
    deform_template_dir = resource_filename('deform', 'templates/')
    deform.Form.set_zpt_renderer(deform_template_dir, translator=translator)
    config = Configurator(settings=settings)
    config.add_static_view('static', 'pyquiz:static')
    config.add_static_view('static_deform', 'deform:static')
    config.add_route('home', '/', view='pyquiz.views.my_view',
                     view_renderer='templates/mytemplate.pt')
    config.add_route('form', '/form', view='pyquiz.views.test_form',
                     view_renderer='templates/forms.pt')
    config.add_route('test', '/test', view='pyquiz.views.test',
                     view_renderer='templates/test.pt')
    config.add_translation_dirs('pyquiz:locale', 'colander:locale', 'deform:locale')
    config.scan('pyquiz')
    return config.make_wsgi_app()
