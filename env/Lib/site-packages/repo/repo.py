# coding: utf-8


class Repo(object):
    def __init__(self, args, config=None):
        self._args = args
        self._config = config

    def show(self):
        print('args', self._args)
