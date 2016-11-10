import os
import unittest
import time
try:
    from importlib import reload
except ImportError:
    pass
import logging

logging.basicConfig(level=logging.DEBUG)

os.environ['DEPFLOW_CACHE'] = '.depflow-test.sqlite3'

import depflow
from plumbum.cmd import cp, cat, touch, rm, echo


def flow():
    run = [False, False, False]

    @depflow.depends(depflow.file_hash('a.txt'))
    def process_a():
        cp('a.txt', 'a')
        run[0] = True

    @depflow.depends(depflow.nofile('b'))
    def process_b():
        touch('b')
        run[1] = True

    @depflow.depends(process_a, process_b, depflow.file_hash('c.txt'))
    def process_c():
        cp('c.txt', 'c')
        (cat['a', 'b', 'c'] > 'done')()
        run[2] = True

    return run[0], run[1], run[2]


class TestDepflow(unittest.TestCase):
    def setUp(self):
        global depflow
        depflow = reload(depflow)

    def test_missing_all(self):
        try:
            a, b, c = flow()
        except:
            pass

    def test_missing_some(self):
        touch('a.txt')

        try:
            a, b, c = flow()
        except:
            pass

    def test_complete(self):
        touch('a.txt')

        try:
            a, b, c = flow()
        except:
            pass

        touch('c.txt')
        a, b, c = flow()
        self.assertFalse(a)
        self.assertFalse(b)
        self.assertTrue(c)

    def test_okay(self):
        touch('a.txt')
        touch('c.txt')

        a, b, c = flow()
        self.assertTrue(a)
        self.assertTrue(b)
        self.assertTrue(c)

    def test_no_work(self):
        touch('a.txt')
        touch('c.txt')

        flow()

        a, b, c = flow()
        self.assertFalse(a)
        self.assertFalse(b)
        self.assertFalse(c)

    def test_rebuild_a(self):
        touch('a.txt')
        touch('c.txt')

        flow()

        (echo['junk'] > 'a.txt')()
        a, b, c = flow()
        self.assertTrue(a)
        self.assertFalse(b)
        self.assertTrue(c)

    def test_no_rebuild_b(self):
        touch('a.txt')
        touch('c.txt')

        flow()

        touch('b')
        a, b, c = flow()
        self.assertFalse(a)
        self.assertFalse(b)
        self.assertFalse(c)

    def test_rebuild_b(self):
        touch('a.txt')
        touch('c.txt')

        flow()

        rm('b')
        a, b, c = flow()
        self.assertFalse(a)
        self.assertTrue(b)
        self.assertTrue(c)

    def test_timestamp_no_rebuild(self):
        touch('a.txt')

        run = [False]

        @depflow.depends(depflow.file('a.txt'))
        def update():
            run[0] = True
        self.assertTrue(run[0])

        run = [False]

        @depflow.depends(depflow.file('a.txt'))  # noqa
        def update():
            run[0] = True
        self.assertFalse(run[0])

    def test_timestamp_rebuild(self):
        touch('a.txt')

        @depflow.depends(depflow.file('a.txt'))
        def update():
            pass
        self.assertTrue(update)

        time.sleep(1)
        touch('a.txt')

        run = [False]

        @depflow.depends(depflow.file('a.txt'))
        def update():
            run[0] = True
        self.assertTrue(run[0])

    def tearDown(self):
        rm('a.txt', retcode=None)
        rm('a', retcode=None)
        rm('b', retcode=None)
        rm('c.txt', retcode=None)
        rm('c', retcode=None)
        rm('done', retcode=None)
        rm('.depflow-test.sqlite3', retcode=None)
