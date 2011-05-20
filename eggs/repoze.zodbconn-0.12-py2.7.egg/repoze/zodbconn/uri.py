
import urlparse
from repoze.zodbconn.resolvers import RESOLVERS

def db_from_uri(uri):
    """Create a database from a list of database URIs and return it.

    uri can be either a whitespace-delimited string or a list of URIs
    as strings.
    """
    if isinstance(uri, basestring):
        uris = uri.strip().split()
    else:
        uris = uri
    databases = {}
    res = None
    for uri in uris:
        dbfactory = dbfactory_from_uri(uri)
        db = dbfactory()
        for name in db.databases:
            if name in databases:
                raise ValueError("database_name %r already in databases" %
                    name)
        # link the databases together
        databases.update(db.databases)
        db.databases = databases
        if res is None:
            # the first database in the list of URIs is the root
            res = db
    return res

def dbfactory_from_uri(uri):
    (scheme, netloc, path, query, frag) = urlparse.urlsplit(uri)
    resolver =  RESOLVERS.get(scheme)
    if resolver is None:
        raise ValueError('Unresolveable URI %s' % uri)
    _, _, _, dbfactory = resolver(uri)
    return dbfactory

