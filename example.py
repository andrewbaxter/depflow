#!/bin/env python
import logging

logging.basicConfig(level=logging.DEBUG)

import depflow
from plumbum.cmd import cp, cat


@depflow.depends(depflow.file('a.txt'))
def step_a():
    cp('a.txt', 'a')


@depflow.depends(depflow.file('b.txt'))
def step_b():
    cp('b.txt', 'b')


@depflow.depends(step_a, step_b, depflow.file('c.txt'))
def step_c():
    cp('c.txt', 'c')
    (cat['a', 'b', 'c'] > 'done')()
