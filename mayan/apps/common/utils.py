from __future__ import unicode_literals

import logging
import os
import shutil
import tempfile

from django.conf import settings
from django.db.models.constants import LOOKUP_SEP
from django.urls import resolve as django_resolve
from django.urls.base import get_script_prefix
from django.utils.datastructures import MultiValueDict
from django.utils.http import urlencode as django_urlencode
from django.utils.http import urlquote as django_urlquote
from django.utils.module_loading import import_string
from django.utils.six.moves import reduce as reduce_function
from django.utils.six.moves import xmlrpc_client

import mayan

from .exceptions import NotLatestVersion, UnknownLatestVersion
from .literals import DJANGO_SQLITE_BACKEND, MAYAN_PYPI_NAME, PYPI_URL
from .settings import setting_temporary_directory

logger = logging.getLogger(__name__)


def check_for_sqlite():
    return settings.DATABASES['default']['ENGINE'] == DJANGO_SQLITE_BACKEND and settings.DEBUG is False


def check_version():
    pypi = xmlrpc_client.ServerProxy(PYPI_URL)
    versions = pypi.package_releases(MAYAN_PYPI_NAME)
    if not versions:
        raise UnknownLatestVersion
    else:
        if versions[0] != mayan.__version__:
            raise NotLatestVersion(upstream_version=versions[0])


# http://stackoverflow.com/questions/123198/how-do-i-copy-a-file-in-python
def copyfile(source, destination, buffer_size=1024 * 1024):
    """
    Copy a file from source to dest. source and dest
    can either be strings or any object with a read or
    write method, like StringIO for example.
    """
    source_descriptor = get_descriptor(source)
    destination_descriptor = get_descriptor(destination, read=False)

    while True:
        copy_buffer = source_descriptor.read(buffer_size)
        if copy_buffer:
            destination_descriptor.write(copy_buffer)
        else:
            break

    source_descriptor.close()
    destination_descriptor.close()


def encapsulate(function):
    # Workaround Django ticket 15791
    # Changeset 16045
    # http://stackoverflow.com/questions/6861601/
    # cannot-resolve-callable-context-variable/6955045#6955045
    return lambda: function


def fs_cleanup(filename, file_descriptor=None, suppress_exceptions=True):
    """
    Tries to remove the given filename. Ignores non-existent files
    """
    if file_descriptor:
        os.close(file_descriptor)

    try:
        os.remove(filename)
    except OSError:
        try:
            shutil.rmtree(filename)
        except OSError:
            if suppress_exceptions:
                pass
            else:
                raise


def get_descriptor(file_input, read=True):
    try:
        # Is it a file like object?
        file_input.seek(0)
    except AttributeError:
        # If not, try open it.
        if read:
            return open(file_input, mode='rb')
        else:
            return open(file_input, mode='wb')
    else:
        return file_input


def get_storage_subclass(dotted_path):
    """
    Import a storage class and return a subclass that will always return eq
    True to avoid creating a new migration when for runtime storage class
    changes.
    """
    imported_storage_class = import_string(dotted_path=dotted_path)

    class StorageSubclass(imported_storage_class):
        def __init__(self, *args, **kwargs):
            return super(StorageSubclass, self).__init__(*args, **kwargs)

        def __eq__(self, other):
            return True

        def deconstruct(self):
            return ('mayan.apps.common.classes.FakeStorageSubclass', (), {})


    return StorageSubclass


def TemporaryFile(*args, **kwargs):
    kwargs.update({'dir': setting_temporary_directory.value})
    return tempfile.TemporaryFile(*args, **kwargs)


def mkdtemp(*args, **kwargs):
    kwargs.update({'dir': setting_temporary_directory.value})
    return tempfile.mkdtemp(*args, **kwargs)


def mkstemp(*args, **kwargs):
    kwargs.update({'dir': setting_temporary_directory.value})
    return tempfile.mkstemp(*args, **kwargs)


def resolve(path, urlconf=None):
    path = '/{}'.format(path.replace(get_script_prefix(), '', 1))
    return django_resolve(path=path, urlconf=urlconf)


def resolve_attribute(obj, attribute, kwargs=None):
    if not kwargs:
        kwargs = {}

    # Try as a callable
    try:
        return attribute(obj, **kwargs)
    except TypeError:
        # Try as a dictionary
        try:
            return obj[attribute]
        except TypeError:
            try:
                # If there are dots in the attribute name, traverse them
                # to the final attribute
                result = reduce_function(getattr, attribute.split('.'), obj)
                try:
                    # Try it as a method
                    return result(**kwargs)
                except TypeError:
                    # Try it as a property
                    return result
            except AttributeError:
                # Try as a related model field
                if LOOKUP_SEP in attribute:
                    attribute_replaced = attribute.replace(LOOKUP_SEP, '.')
                    return resolve_attribute(
                        obj=obj, attribute=attribute_replaced, kwargs=kwargs
                    )
                else:
                    raise


def return_related(instance, related_field):
    """
    This functions works in a similar method to resolve_attribute but is
    meant for related models. Support multiple levels of relationship
    using double underscore.
    """
    return reduce_function(getattr, related_field.split('__'), instance)


def urlquote(link=None, get=None):
    """
    This method does both: urlquote() and urlencode()

    urlqoute(): Quote special characters in 'link'

    urlencode(): Map dictionary to query string key=value&...

    HTML escaping is not done.

    Example:

    urlquote('/wiki/Python_(programming_language)')
        --> '/wiki/Python_%28programming_language%29'
    urlquote('/mypath/', {'key': 'value'})
        --> '/mypath/?key=value'
    urlquote('/mypath/', {'key': ['value1', 'value2']})
        --> '/mypath/?key=value1&key=value2'
    urlquote({'key': ['value1', 'value2']})
        --> 'key=value1&key=value2'
    """
    if get is None:
        get = []

    assert link or get
    if isinstance(link, dict):
        # urlqoute({'key': 'value', 'key2': 'value2'}) -->
        # key=value&key2=value2
        assert not get, get
        get = link
        link = ''
    assert isinstance(get, dict), 'wrong type "%s", dict required' % type(get)
    # assert not (link.startswith('http://') or link.startswith('https://')),
    #    'This method should only quote the url path.
    #    It should not start with http(s)://  (%s)' % (
    #    link)
    if get:
        # http://code.djangoproject.com/ticket/9089
        if isinstance(get, MultiValueDict):
            get = get.lists()
        if link:
            link = '%s?' % django_urlquote(link)
        return '%s%s' % (link, django_urlencode(get, doseq=True))
    else:
        return django_urlquote(link)


def validate_path(path):
    if not os.path.exists(path):
        # If doesn't exist try to create it
        try:
            os.mkdir(path)
        except Exception as exception:
            logger.debug('unhandled exception: %s', exception)
            return False

    # Check if it is writable
    try:
        fd, test_filepath = tempfile.mkstemp(dir=path)
        os.close(fd)
        os.unlink(test_filepath)
    except Exception as exception:
        logger.debug('unhandled exception: %s', exception)
        return False

    return True
