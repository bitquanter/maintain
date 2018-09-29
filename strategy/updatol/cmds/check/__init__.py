#!/usr/bin/env python
#coding:utf-8

from .check_bcolz_data import check_bcolz_data

check_commands = [
    check_bcolz_data,
]

__all__ = [
    str(cmd.name) for cmd in check_commands
]
