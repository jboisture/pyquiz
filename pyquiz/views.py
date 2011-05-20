from pyramid.view import view_config
from pyquiz.resources import MyResource

@view_config(context=MyResource, renderer='pyquiz:templates/mytemplate.pt')
def my_view(request):
    return {'project':'pyquiz'}
