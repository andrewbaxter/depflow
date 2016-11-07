#!/bin/env python
import logging

logging.basicConfig(level=logging.DEBUG)

import depflow
from plumbum.cmd import cp, cat


@depflow.depends(depflow.file('a.txt'))
def process_a():
    cp('a.txt', 'a')


@depflow.depends(depflow.file('b.txt'))
def process_b():
    cp('b.txt', 'b')


@depflow.depends(process_a, process_b, depflow.file('c.txt'))
def process_c():
    cp('c.txt', 'c')
    cat['a', 'b', 'c'] > 'done'
