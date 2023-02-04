# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import

import subprocess

from ruamel.std.pathlib import Path


def check_output(*args, **kw):
    """make sure all args parameters are strings and that
    the output is unicode"""
    args = list(args)
    args[0] = [str(x) for x in args[0]]
    if 'stderr' not in kw:
        kw['stderr'] = subprocess.STDOUT
    res = subprocess.check_output(*args, **kw)
    # print('check_output res', repr(res))
    return res.decode('utf-8')


def check_output_utf8(*args, **kw):
    """make sure all args parameters are strings and that
    the output is unicode"""
    args = list(args)
    kwc = kw.copy()
    args[0] = [str(x) for x in args[0]]
    if 'stderr' not in kwc:
        kwc['stderr'] = subprocess.STDOUT
    if 'encoding' not in kwc:
        kwc['encoding'] = 'utf-8'
    return subprocess.check_output(*args, **kwc)


def unclean_list(directory=None):
    if directory is None:
        directory = Path('.')
    res = check_output(['hg', 'status', directory])
    found = []
    for line in res.splitlines():
        assert line[1] == u' '
        if line[0] not in 'MARCI':
            found.append(line)
    return found


def is_clean(directory=None):
    return unclean_list(directory) == []


def status_list(directory=None):
    if directory is None:
        directory = Path('.')
    res = check_output(['hg', 'status', directory])
    found = []
    for line in res.splitlines():
        assert line[1] == u' '
        found.append(line)
    return found
