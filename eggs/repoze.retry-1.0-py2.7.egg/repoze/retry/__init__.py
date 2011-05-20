# repoze retry-on-conflict-error behavior
import itertools
import socket
from tempfile import TemporaryFile
import traceback
from StringIO import StringIO

# Avoid hard dependency on ZODB.
try:
    from ZODB.POSException import ConflictError
except ImportError:
    class ConflictError(Exception):
        pass

# Avoid hard dependency on Zope2.
try:
    from ZPublisher.Publish import Retry as RetryException
except ImportError:
    class RetryException(Exception):
        pass

class Retry:
    def __init__(self, application, tries, retryable=None, highwater=2<<20):
        """ WSGI Middlware which retries a configurable set of exception types.

        o 'application' is the RHS in the WSGI "pipeline".

        o 'retries' is the maximun number of times to retry a request.

        o 'retryable' is a sequence of one or more exception types which,
          if raised, indicate that the request should be retried.

        o
        """
        self.application = application
        self.tries = tries

        if retryable is None:
            retryable = (ConflictError, RetryException,)

        if not isinstance(retryable, (list, tuple)):
            retryable = [retryable]

        self.retryable = tuple(retryable)
        self.highwater = highwater

    def __call__(self, environ, start_response):
        catch_response = []
        written = []
        original_wsgi_input = environ.get('wsgi.input')
        new_wsgi_input = None

        if original_wsgi_input is not None:
            cl = environ.get('CONTENT_LENGTH', '0')
            cl = int(cl)
            if cl > self.highwater:
                new_wsgi_input = environ['wsgi.input'] = TemporaryFile('w+b')
            else:
                new_wsgi_input = environ['wsgi.input'] = StringIO()
            rest = cl
            chunksize = 1<<20
            try:
                while rest:
                    if rest <= chunksize:
                        chunk = original_wsgi_input.read(rest)
                        rest = 0
                    else:
                        chunk = original_wsgi_input.read(chunksize)
                        rest = rest - chunksize
                    new_wsgi_input.write(chunk)
            except (socket.error, IOError):
                # Different wsgi servers will generate either socket.error or
                # IOError if there is a problem reading POST data from browser.
                msg = 'Not enough data in request or socket error'
                start_response('400 Bad Request', [
                    ('Content-Type', 'text/plain'),
                    ('Content-Length', str(len(msg))),
                    ]
                )
                return [msg]
            new_wsgi_input.seek(0)

        def replace_start_response(status, headers, exc_info=None):
            catch_response[:] = [status, headers, exc_info]
            return written.append

        i = 0
        while 1:
            try:
                app_iter = self.application(environ, replace_start_response)
            except self.retryable, e:
                i += 1
                errors = environ.get('wsgi.errors')
                if errors is not None:
                    errors.write('repoze.retry retrying, count = %s\n' % i)
                    traceback.print_exc(None, errors)
                if i < self.tries:
                    if new_wsgi_input is not None:
                        new_wsgi_input.seek(0)
                    catch_response[:] = []
                    continue
                if catch_response:
                    start_response(*catch_response)
                raise
            else:
                if catch_response:
                    start_response(*catch_response)
                else:
                    if hasattr(app_iter, 'close'):
                        app_iter.close()
                    raise AssertionError('app must call start_response before '
                                         'returning')
                return close_when_done_generator(written, app_iter)

def close_when_done_generator(written, app_iter):
    for chunk in itertools.chain(written, app_iter):
        yield chunk
    if hasattr(app_iter, 'close'):
        app_iter.close()

def make_retry(app, global_conf, **local_conf):
    from pkg_resources import EntryPoint
    tries = int(local_conf.get('tries', 3))
    retryable = local_conf.get('retryable')
    highwater = local_conf.get('highwater', 2<<20)
    if retryable is not None:
        retryable = [EntryPoint.parse('x=%s' % x).load(False)
                      for x in retryable.split(' ')]
    return Retry(app, tries, retryable=retryable, highwater=highwater)
