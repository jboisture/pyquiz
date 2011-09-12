from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.security import forget
from pyramid.security import unauthenticated_userid
from pyramid.security import authenticated_userid
from pyramid.url import route_url
from pyramid.renderers import get_renderer
from pyquiz.models import DBSession, Term, Section

from pyquiz.security import USERS
from xmlrpclib import ServerProxy
from __init__ import trans, serverLocation

def schooltool_login(username, password,user_info):
    """
    This method gets information from schooltool about a users courses and their role
    """
    server = ServerProxy(serverLocation, transport = trans)
    dbsession = DBSession()
    courses = []
    for course in user_info['courses']:
        name = user_info['first_name']+" "+user_info['last_name']
        sections = dbsession.query(Section).filter(
                               Section.course_id == course[2]).all()
        if len(sections) != 0:
            section = sections[0]
        else:
            if 'teacher' not in user_info['roles']: 
                section = Section(course[5], course[2], course[0], '')
            if 'teacher' in user_info['roles']: 
                section = Section(course[5], course[2], course[0], name)
            print 
            dbsession.add(section)
            dbsession.flush()
        if section.id not in courses:
            courses.append(section.id)
        c = dbsession.query(Term).filter(Term.term_name == course[1]).all()
        if len(c) == 0: 
            new_course = Term(course[4], course[1], section.id)
            dbsession.add(new_course)
            dbsession.flush()
        if len(sections) == 1 and user_info['roles'] == ['teacher']:
            if (len(section.instructor) != 0 and 
                          name not in section.instructor):
                section.instructor += "%&"
                section.instructor += name
            elif len(section.instructor) == 0:
                section.instructor += name
            dbsession.flush()
    user_info['courses'] = courses
    return user_info


def login(request):
    """
    This method lets a user login to pyquiz
    """
    if unauthenticated_userid(request) != None and 'user' in request.session.keys():
        return HTTPFound(location='/index')
    message = ''
    login = ''
    password = ''
    if 'form.submitted' in request.params:
        username = request.params['login']
        password = request.params['password']
        server = ServerProxy(serverLocation, transport = trans)
        if server.login(username, password):
            user_info = server.get_user_info(username)
            userinfo = schooltool_login(username, password, user_info)
            request.session['user'] = userinfo
            headers = remember(request, userinfo['roles'][0])
            return HTTPFound(location='/index',
                             headers = headers)
        message = 'Failed login'

    return dict(
        message = message,
        url = request.application_url + '/',
        login = login,
        password = password,
        main = get_renderer('templates/master.pt').implementation(),
        )
    
def logout(request):
    """
    This method logs a user out of pyquiz
    """
    headers = forget(request)
    if 'user' in request.session.keys():
        request.session.pop('user')
    return HTTPFound(location='/')
