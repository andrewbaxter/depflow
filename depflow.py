import logging
import os
from hashlib import md5
import json
import sqlite3

logger = logging.getLogger('depflow')

os.stat_float_times(False)

_db_name = '.depflow.sqlite3'
_db = sqlite3.connect(_db_name)
logger.debug('Using cache at {}'.format(os.path.abspath(_db_name)))
_db.execute('create table if not exists keyvalue (key text primary key, value text not null)')  # noqa
_db.commit()

_id = ''


def _db_get(key):
    out = _db.execute(
        'select value from keyvalue where key = ?', (key,)).fetchone()
    if out is None:
        return None
    return out[0]


def _db_set(key, value):
    _db.execute(
        'insert or replace into keyvalue (key, value) values (?, ?)',
        (key, value))
    _db.commit()


def flow_id(name):
    global _id
    _id = name


def depends(*nodes):
    '''
    Runs the wrapped function if any dependency has changed.

    Dependency nodes can be either other functions wrapped with depends or
    checks.
    '''
    def wrap_function(function):
        class _Rule(object):
            def __init__(self):
                self._unique = '{} {}'.format(
                    function.__name__,
                    md5(''.join(
                            node.unique() for node in nodes
                        ).encode('utf-8')).hexdigest())
                self._changed = any(node.changed(self) for node in nodes)
                if self._changed:
                    logger.debug('Running {}'.format(function.__name__))
                    function()
                    for node in nodes:
                        node.commit_changed(self)

            def unique(self):
                return self._unique

            def changed(self, base):
                return self._changed

            def commit_changed(self, base):
                pass

        return _Rule()
    return wrap_function


def check(function):
    '''
    Converts a function that returns a key, value into a function that can be
    used as a dependency.

    The key should be a unique id for the object being checked.
    The value should be a value representing the state of the object.
    '''
    def inner(*pargs, **kwargs):
        k, v = function(*pargs, **kwargs)
        v = str(v)

        class _Check(object):
            def unique(self):
                return k

            def changed(self, base):
                k2 = json.dumps([_id, k, base.unique()])
                v_old = _db_get(k2)
                if v == v_old:
                    return False
                return True

            def commit_changed(self, base):
                k2 = json.dumps([_id, k, base.unique()])
                _db_set(k2, v)

        return _Check()
    return inner


@check
def file(path):
    '''Check for changes in a single file.'''
    try:
        return path, os.path.getmtime(path)
    except FileNotFoundError:
        return path, 0


@check
def tree(path):
    '''Check for changes in a file tree.'''
    if not path.endswith('/'):
        path = path + '/'
    value = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            value += os.path.getmtime(os.path.join(root, file))
    return path, value
