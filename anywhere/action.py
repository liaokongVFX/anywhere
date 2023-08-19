# -*- coding: utf-8 -*-
import os
import inspect

EMPTY = 0
TEXT = 1
MULT_FILES = 2
FILE = 3


class ActionBase(object):
    name = ''
    description = ''
    shortcut = None
    icon = None
    action_types = []

    def __init__(self):
        self.__NEED_REGISTER__ = True
        self._verify_required_fields()

    def run(self, context):
        return NotImplementedError

    @property
    def icon_path(self):
        if self.icon:
            return os.path.join(os.path.dirname(inspect.getfile(self.__class__)), self.icon)
        return ''

    def _verify_required_fields(self):
        for field in ['name', 'description', 'action_types']:
            if not getattr(self, field):
                raise ValueError('字段 {} 是必须设置的')
