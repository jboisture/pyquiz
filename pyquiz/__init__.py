from pkg_resources import resource_filename
from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from sqlalchemy.pool import NullPool

from pyquiz.models import initialize_sql

from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.i18n import get_localizer
from pyramid.threadlocal import get_current_request

import deform



def translator(term):
    return get_localizer(get_current_request()).translate(term)



def main(global_config, **settings):
    """ 
    This function returns a Pyramid WSGI application.
    Sets up all routes connecteing views and templates.
    """
    engine = engine_from_config(settings, 'sqlalchemy.',poolclass=NullPool)
    initialize_sql(engine)
    deform_template_dir = resource_filename('deform', 'templates/')
    deform.Form.set_zpt_renderer(deform_template_dir, translator=translator)
    my_session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')
    config = Configurator(settings=settings, 
                          session_factory = my_session_factory)
    config.add_static_view('static', 'pyquiz:static')
    config.add_static_view('static_deform', 'deform:static')
    config.add_route('index', '/', view='pyquiz.views.view_index',
                     view_renderer='templates/index.pt')
    config.add_route('create test', '/create_test',   
                     view='pyquiz.views.view_create_test',
                     view_renderer='templates/create_test.pt')
    config.add_route('question', '/question', view='pyquiz.views.view_question',
                     view_renderer='templates/question.pt')
    config.add_route('test', '/test', view='pyquiz.views.view_test',
                     view_renderer='templates/test.pt')
    config.add_route('grade', '/grade', view='pyquiz.views.view_grade_test',
                     view_renderer='templates/grade_test.pt')
    config.add_route('choose test', '/choose_test', view='pyquiz.views.view_choose_test',
                     view_renderer='templates/choose_test.pt')
    config.add_route('edit test', '/edit_test', view='pyquiz.views.view_edit_test',
                     view_renderer='templates/edit_test.pt')
    config.add_route('edit question', '/edit_question', view='pyquiz.views.view_edit_question',
                     view_renderer='templates/edit_question.pt')
    config.add_translation_dirs('pyquiz:locale', 'colander:locale', 'deform:locale')
    config.scan('pyquiz')
    return config.make_wsgi_app()
