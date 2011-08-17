from pkg_resources import resource_filename
from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from sqlalchemy.pool import NullPool

from pyquiz.models import initialize_sql

from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.i18n import get_localizer
from pyramid.threadlocal import get_current_request

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyquiz.security import groupfinder

import deform



def translator(term):
    return get_localizer(get_current_request()).translate(term)



def main(global_config, **settings):
    """ 
    This function returns a Pyramid WSGI application.
    Sets up all routes connecting views and templates.
    """
    engine = engine_from_config(settings, 'sqlalchemy.',poolclass=NullPool)
    initialize_sql(engine)
    deform_template_dir = resource_filename('deform', 'templates/')
    deform.Form.set_zpt_renderer(deform_template_dir, translator=translator)
    my_session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')
    authn_policy = AuthTktAuthenticationPolicy(
        'sosecret', callback=groupfinder)
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(settings=settings,
                          root_factory='pyquiz.models.RootFactory',
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy,
                          session_factory = my_session_factory)
    config.add_static_view('static', 'pyquiz:static')
    config.add_static_view('static_deform', 'deform:static')
    config.add_route('login', '/', view='pyquiz.login.login',
                     view_renderer='pyquiz:templates/login.pt')
    config.add_route('index', '/index', view='pyquiz.views.view_index',
                     view_renderer='templates/index.pt')
    config.add_route('create test', '/create_test',   
                     view='pyquiz.views.view_create_test',
                     view_renderer='templates/create_test.pt')
    config.add_route('change dates', '/change_dates',   
                     view='pyquiz.views.view_change_dates',
                     view_renderer='templates/create_test.pt')
    config.add_route('grade submitted test', '/grade_submitted_test',   
                     view='pyquiz.views.view_grade_submitted_test',
                     view_renderer='templates/grade_submitted_test.pt')
    config.add_route('grade question', '/grade_question',   
                     view='pyquiz.views.view_grade_question',
                     view_renderer='templates/grade_question.pt')
    config.add_route('ungraded tests', '/ungraded_tests', view='pyquiz.views.view_ungraded_tests',
                     view_renderer = 'templates/ungraded_tests.pt')
    config.add_route('question', '/question',            
                     view='pyquiz.views.view_question',
                     view_renderer='templates/question.pt')
    config.add_route('test', '/test', view='pyquiz.views.view_test',
                     view_renderer='templates/test.pt')
    config.add_route('course', '/course', view='pyquiz.views.view_course',
                     view_renderer='templates/course.pt')
    config.add_route('course teacher', '/course_teacher', 
                     view='pyquiz.views.view_course_teacher',
                     view_renderer='templates/course_teacher.pt')
    config.add_route('grade', '/grade', view='pyquiz.views.view_grade_test',
                     view_renderer='templates/grade_test.pt')
    config.add_route('edit test', '/edit_test', 
                     view='pyquiz.views.view_edit_test',
                     view_renderer='templates/edit_test.pt')
    config.add_route('edit question', '/edit_question', 
                     view='pyquiz.views.view_edit_question',
                     view_renderer='templates/edit_question.pt')
    config.add_route('delete test', '/delete_test', 
                     view='pyquiz.views.view_delete_test',
                     view_renderer='templates/delete_test.pt')
    config.add_route('add questions', '/add_questions', 
                     view='pyquiz.views.view_add_questions',
                     view_renderer='templates/add_questions.pt')
    config.add_translation_dirs('pyquiz:locale', 
                                'colander:locale',
                                'deform:locale')
    config.add_view('pyquiz.login.login',
                    context='pyramid.httpexceptions.HTTPForbidden',
                    renderer='pyquiz:templates/login.pt')
    config.add_route('logout', '/logout')
    config.add_view('pyquiz.login.logout', route_name='logout')
    config.scan('pyquiz')
    return config.make_wsgi_app()
