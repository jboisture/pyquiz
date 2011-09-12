# http://blog.godson.in/2010/09/how-to-make-python-xmlrpclib-client.html
#
"""
These transports store a session cookie and send it with each request
"""

from xmlrpclib import Transport, SafeTransport, ProtocolError


class SessionTransportBase(Transport):
    
    session = ''
    
    def __init__(self):
        Transport.__init__(self, use_datetime=0)
    
    def request(self, host, handler, request_body, verbose=0):
        # issue XML-RPC request
        h = self.make_connection(host)
        if verbose:
            h.set_debuglevel(1)
        self.send_request(h, handler, request_body)
        self.send_host(h, host)
        self.send_user_agent(h)
        self.send_content(h, request_body)
        response = h.getresponse()
        self.session = response.getheader("Set-Cookie",
                                         self.session).split(";")[0]
        """if errcode != 200:
            raise ProtocolError(
                host + handler,
                errcode, errmsg,
                headers
                )"""
        self.verbose = verbose
        try:
            sock = h.sock
        except AttributeError:
            sock = None
        return self.parse_response(response)
      
    def send_user_agent(self, connection):
        if self.session:          
            connection.putheader("Cookie", self.session)
        return Transport.send_user_agent(self, connection)


class SessionTransport(SessionTransportBase, Transport): pass

class SessionSafeTransport(SessionTransportBase, SafeTransport): pass
