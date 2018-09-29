#!/usr/bin/env python
#coding:utf-8

from .look_bcolz_data import look_bcolz_data
from .look_bcolz_day import look_bcolz_day
from .look_bcolz_minute import look_bcolz_minute

look_commands = [
    look_bcolz_data,
    look_bcolz_day,
    look_bcolz_minute,
]

__all__ = [
    str(cmd.name) for cmd in look_commands
]
