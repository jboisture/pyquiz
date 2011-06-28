from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.security import forget
from pyramid.security import unauthenticated_userid
from pyramid.security import authenticated_userid
from pyramid.url import route_url

from pyquiz.models import DBSession, Course

from pyquiz.security import USERS

def schooltool_login(username, password):
    if username == "student":
        user_info = {'username': 'student',
                     'name': 'student student',
                     'role': 'student',
                     'courses': [('101', 'Math 101'),
                                 ('102', 'Math 102')]}
    if username == "teacher":
        user_info = {'username': 'teacher',
                     'name': 'teacher teacher',
                     'role': 'teacher',
                     'courses': [('101', 'Math 101'),
                                 ('102', 'Math 102'),
                                 ('103', 'Math 103')]}
    if username == "teacher2":
        user_info = {'username': 'teacher2',
                     'name': 'test teacher2',
                     'role': 'teacher',
                     'courses': [('101', 'Math 101'),
                                 ('103', 'Math 103')]}
    dbsession = DBSession()
    for course in user_info['courses']:
        c = dbsession.query(Course).filter(Course.course_id == course[0]).all()
        if len(c) == 0:
            if user_info['role'] != 'teacher':
                 new_course = Course(course[0], course[1], '')
            if user_info['role'] == 'teacher':
                 new_course = Course(course[0], course[1], user_info['name'])
            dbsession.add(new_course)
            dbsession.flush()
        if len(c) == 1 and user_info['role'] == 'teacher':
            if (len(c[0].instructor) != 0 and 
                          user_info['name'] not in c[0].instructor):
                c[0].instructor += "%&"
                c[0].instructor += user_info['name']
            elif len(c[0].instructor) == 0:
                c[0].instructor += user_info['name']
            dbsession.flush()
    return user_info


def login(request):
    if unauthenticated_userid(request) != None:
        return HTTPFound(location='/index')
    message = ''
    login = ''
    password = ''
    if 'form.submitted' in request.params:
        username = request.params['login']
        password = request.params['password']
        if USERS.get(username) == password:
            userinfo = schooltool_login(username, password)
            request.session['user'] = userinfo
            headers = remember(request, userinfo['role'])
            return HTTPFound(location='/index',
                             headers = headers)
        message = 'Failed login'

    return dict(
        message = message,
        url = request.application_url + '/',
        login = login,
        password = password,
        )
    
def logout(request):
    headers = forget(request)
    if 'user' in request.session.keys():
        request.session.pop('user')
    return HTTPFound(location='/')
