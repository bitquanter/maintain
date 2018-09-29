#!/usr/bin/env python
#coding:utf-8

from .update_bcolz_day_data import update_bcolz_day_data
from .update_bcolz_minute_data import update_bcolz_minute_data

update_commands = [
    update_bcolz_day_data,
    update_bcolz_minute_data,
]

__all__ = [
    str(cmd.name) for cmd in update_commands
]

