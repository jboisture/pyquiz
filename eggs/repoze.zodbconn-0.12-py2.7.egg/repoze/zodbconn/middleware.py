CLOSER_KEY = 'repoze.zodbconn.closer'

class EnvironmentDeleterMiddleware:
    """ WSGI middleware which deletes a key from the environment if it
    exists (on egress).

    - keyname is the key to delete
    """
    def __init__(self, application, key=CLOSER_KEY):
        self.application = application
        self.key = key

    def __call__(self, environ, start_response):
        try:
            result = self.application(environ, start_response)
            return result
        finally:
            if self.key in environ:
                del environ[self.key]

def make_middleware(app, global_conf, **local_conf):
    key = local_conf.get('key', CLOSER_KEY)
    return EnvironmentDeleterMiddleware(app, key)
