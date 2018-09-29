#!/usr/bin/env python
#coding:utf-8

'''
取数据相关接口
'''
import sys
if sys.version_info[0] == 3:
    xrange = range
    
import datetime
import collections
import os
import six
import pandas as pd
import numpy as np
from .exceptions import ParamsError



EMPTY_ARRAY = np.empty((0,))
nan = NAN = float('nan')
frequency_compat = {
    'daily': '1d',
    'minute': '1m',
}

DEFAULT_FIELDS = ['open', 'close', 'high', 'low', 'volume', 'money']


def my_assert(condition, e=None):
    if not condition:
        if not e:
            e = AssertionError()
        elif isinstance(e, six.string_types):
            e = AssertionError(e)
        elif not isinstance(e, Exception):
            e = AssertionError(str(e))
        raise e


def is_str(s):
    return isinstance(s, six.string_types)


def convert_dt(dt):
    """
    >>> convert_dt(datetime.date(2015, 1, 1))
    datetime.datetime(2015, 1, 1, 0, 0)

    >>> convert_dt(datetime.datetime(2015, 1, 1))
    datetime.datetime(2015, 1, 1, 0, 0)

    >>> convert_dt('2015-1-1')
    datetime.datetime(2015, 1, 1, 0, 0)

    >>> convert_dt('2015-01-01 09:30:00')
    datetime.datetime(2015, 1, 1, 9, 30)

    >>> convert_dt(datetime.datetime(2015, 1, 1, 9, 30))
    datetime.datetime(2015, 1, 1, 9, 30)
    """
    if is_str(dt):
        if ':' in dt:
            return datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
        else:
            return datetime.datetime.strptime(dt, '%Y-%m-%d')
    elif isinstance(dt, datetime.datetime):
        return dt
    elif isinstance(dt, datetime.date):
        return date2dt(dt)
    raise ParamsError("date 必须是datetime.date, datetime.datetime或者如下格式的字符串:'2015-01-05'")


def ensure_str_tuple(args):
    if is_str(args):
        return (args,)
    else:
        atuple = tuple(args)
        for i in atuple:
            assert isinstance(i, six.string_types)
        return atuple


def check_unit_fields(unit, fields):
    count = int(unit[:-1])
    my_assert(unit[-1] in ('d', 'm') and count > 0, 'unit应该是1d/1m, 5d/5m这种数字+d/m的形式')
    if fields:
        if count > 1:
            my_assert(all([(f in DEFAULT_FIELDS) for f in fields]), "查询多天/多分钟的历史数据时, field必须是"+str(DEFAULT_FIELDS)+"中的一个")
        else:
            my_assert(all([(f in ALLOED_FIELDS) for f in fields]), "field必须是"+str(ALLOED_FIELDS)+"中的一个")


def is_list(l):
    return isinstance(l, (list, tuple))


def group_array(a, group, field):
    if group > 1:
        new_int_index = xrange(0, len(a), group)
        grouper = {
            'open': (lambda v: [v[i] for i in new_int_index]),
            'close': (lambda v: [v[min(i+group-1, len(v)-1)] for i in new_int_index]),
            'high': (lambda v: [max(v[i:i+group]) for i in new_int_index]),
            'low': (lambda v: [min(v[i:i+group]) for i in new_int_index]),
            'volume': (lambda v: [sum(v[i:i+group]) for i in new_int_index]),
            'money': (lambda v: [sum(v[i:i+group]) for i in new_int_index]),
            # same to close
            'index': (lambda v: [v[min(i+group-1, len(v)-1)] for i in new_int_index]),
        }
        a = grouper[field](a)
        if not isinstance(a, np.ndarray):
            a = np.array(a)
    return a