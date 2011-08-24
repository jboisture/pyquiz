from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.security import forget
from pyramid.security import unauthenticated_userid
from pyramid.security import authenticated_userid
from pyramid.url import route_url
from pyramid.renderers import get_renderer
from pyquiz.models import DBSession, Course

from pyquiz.security import USERS
from xmlrpclib import ServerProxy
from __init__ import trans, serverLocation

def schooltool_login(username, password,user_info):
    """
    This method gets information from schooltool about a users courses and their role
    """
    server = ServerProxy(serverLocation, transport = trans)
    dbsession = DBSession()
    for course in user_info['courses']:
        c = dbsession.query(Course).filter(Course.course_id == course[1]).all()
        if len(c) == 0: 
            if 'teacher' not in user_info['roles']: 
                 new_course = Course(course[0], course[1], course[2], '')
            if 'teacher' in user_info['roles']:
                 new_course = Course(course[0], course[1], course[2], user_info['name'])
            dbsession.add(new_course)
            dbsession.flush()
        if len(c) == 1 and user_info['roles'] == ['teacher']:
            if (len(c[0].instructor) != 0 and 
                          user_info['name'] not in c[0].instructor):
                c[0].instructor += "%&"
                c[0].instructor += user_info['name']
            elif len(c[0].instructor) == 0:
                c[0].instructor += user_info['name']
            dbsession.flush()
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
