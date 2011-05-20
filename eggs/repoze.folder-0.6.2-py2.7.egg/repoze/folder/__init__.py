import sys

from zope.interface import implements

from zope.component.event import objectEventNotify

from persistent import Persistent

from repoze.folder.interfaces import IFolder
from repoze.folder.interfaces import marker

from repoze.folder.events import ObjectAddedEvent
from repoze.folder.events import ObjectWillBeAddedEvent
from repoze.folder.events import ObjectRemovedEvent
from repoze.folder.events import ObjectWillBeRemovedEvent

from BTrees.OOBTree import OOBTree
from BTrees.Length import Length

sysencoding = sys.getdefaultencoding()

class Folder(Persistent):
    """ A folder implementation which acts much like a Python dictionary.

    keys are Unicode strings; values are arbitrary Python objects.
    """

    # _num_objects=None below is b/w compat for older instances of
    # folders which don't have a BTrees.Length object as a
    # _num_objects attribute.
    _num_objects = None 

    __name__ = None
    __parent__ = None

    # Default uses ordering of underlying BTree.
    _order = None
    def _get_order(self):
        if self._order is not None:
            return list(self._order)
        return self.data.keys()
    def _set_order(self, value):
        # XXX:  should we test against self.data.keys()?
        self._order = tuple([unicodify(x) for x in value])
    def _del_order(self):
        del self._order
    order = property(_get_order, _set_order, _del_order)

    implements(IFolder)

    def __init__(self, data=None):
        if data is None:
            data = {}
        self.data = OOBTree(data)
        self._num_objects = Length(len(data))

    def keys(self):
        """ See IFolder.
        """
        return self.order

    def __iter__(self):
        return iter(self.order)

    def values(self):
        """ See IFolder.
        """
        if self._order is not None:
            return [self.data[name] for name in self.order]
        return self.data.values()

    def items(self):
        """ See IFolder.
        """
        if self._order is not None:
            return [(name, self.data[name]) for name in self.order]
        return self.data.items()

    def __len__(self):
        """ See IFolder.
        """
        if self._num_objects is None:
            # can be arbitrarily expensive
            return len(self.data)
        return self._num_objects()

    def __nonzero__(self):
        """ See IFolder.
        """
        return True

    def __getitem__(self, name):
        """ See IFolder.
        """
        name = unicodify(name)
        return self.data[name]

    def get(self, name, default=None):
        """ See IFolder.
        """
        name = unicodify(name)
        return self.data.get(name, default)

    def __contains__(self, name):
        """ See IFolder.
        """
        name = unicodify(name)
        return self.data.has_key(name)

    def __setitem__(self, name, other):
        """ See IFolder.
        """
        return self.add(name, other)

    def add(self, name, other, send_events=True):
        """ See IFolder.
        """
        if not isinstance(name, basestring):
            raise TypeError("Name must be a string rather than a %s" %
                            name.__class__.__name__)
        if not name:
            raise TypeError("Name must not be empty")

        name = unicodify(name)

        if self.data.has_key(name):
            raise KeyError('An object named %s already exists' % name)

        if send_events:
            objectEventNotify(ObjectWillBeAddedEvent(other, self, name))
        other.__parent__ = self
        other.__name__ = name

        # backwards compatibility: add a Length _num_objects to folders that
        # have none
        if self._num_objects is None:
            self._num_objects = Length(len(self.data))

        self.data[name] = other
        self._num_objects.change(1)

        if self._order is not None:
            self._order += (name,)

        if send_events:
            objectEventNotify(ObjectAddedEvent(other, self, name))

    def __delitem__(self, name):
        """ See IFolder.
        """
        return self.remove(name)

    def remove(self, name, send_events=True):
        """ See IFolder.
        """
        name = unicodify(name)
        other = self.data[name]

        if send_events:
            objectEventNotify(ObjectWillBeRemovedEvent(other, self, name))

        if hasattr(other, '__parent__'):
            del other.__parent__

        if hasattr(other, '__name__'):
            del other.__name__

        # backwards compatibility: add a Length _num_objects to folders that
        # have none
        if self._num_objects is None:
            self._num_objects = Length(len(self.data))

        del self.data[name]
        self._num_objects.change(-1)

        if self._order is not None:
            self._order = tuple([x for x in self._order if x != name])

        if send_events:
            objectEventNotify(ObjectRemovedEvent(other, self, name))

        return other

    def pop(self, name, default=marker):
        """ See IFolder.
        """
        try:
            result = self.remove(name)
        except KeyError:
            if default is marker:
                raise
            return default
        return result

    def __repr__(self):
        klass = self.__class__
        classname = '%s.%s' % (klass.__module__, klass.__name__)
        return '<%s object %r at %#x>' % (classname,
                                          self.__name__,
                                          id(self))
    
def unicodify(name, encoding=None):
    if encoding is None:
        encoding = sysencoding
    try:
        name = unicode(name)
    except UnicodeError:
        if encoding in ('utf-8', 'utf8'):
            raise TypeError(
                'Byte string names must be decodeable using the system '
                'encoding of "utf-8" (%s)' % name
                )
        try:
            name = unicode(name, 'utf-8')
        except UnicodeError:
            raise TypeError(
                'Byte string names must be decodeable using either the system '
                'encoding of "%s" or the "utf-8" encoding (%s)' % (
                sysencoding, name)
                )

    return name

