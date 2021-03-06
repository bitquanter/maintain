# -*- coding: utf-8 -*-

from __future__ import absolute_import
import os
import datetime
import six
import collections


NaN = NAN = nan = float('nan')

TRADE_MIN_DATE = datetime.date(2009, 1, 4)
TRADE_MAX_DATE = datetime.date(9999, 1, 1)


def fixed_round(x, n=2):
    # 速度比np.round快
    assert n <= 4
    _pow10 = (1, 10, 100, 1000, 10000)
    return round(x * _pow10[n]) / _pow10[n]

def is_str(obj):
    return isinstance(obj, six.string_types)



def is_lists(obj):
    return isinstance(obj, (list, tuple))


def is_iterable(obj):
    return isinstance(obj, collections.Iterable)


def obj_to_tuple(obj):
    """把任何对象都转化为元组"""
    if is_str(obj):
        return (obj,)
    elif is_iterable(obj):
        return tuple(obj)
    else:
        return (obj,)


def check_string(s):
    if not is_str(s):
        raise Exception("参数必须是个字符串, 实际是:s=%s type(s)=%s" %(str(s), type(s)))


def check_lists(l):
    if type(l) not in (tuple, list):
        raise Exception("参数必须是tuple或者list, 实际是:" + str(l))


def check_string_list(seq):
    check_lists(seq)
    for item in seq:
        check_string(item)


def date2dt(date):
    """将 datetime.date 转化为 datetime.datetime"""
    return datetime.datetime.combine(date, datetime.time.min)


def convert_date(date):
    """
    >>> convert_date('2015-1-1')
    datetime.date(2015, 1, 1)

    >>> convert_date('2015-01-01 00:00:00')
    datetime.date(2015, 1, 1)

    >>> convert_date(datetime.datetime(2015, 1, 1))
    datetime.date(2015, 1, 1)

    >>> convert_date(datetime.date(2015, 1, 1))
    datetime.date(2015, 1, 1)
    """
    from pandas import Timestamp
    if isinstance(date, Timestamp):
        date = str(date)
    if is_str(date):
        if ':' in date:
            date = date[:10]
        return datetime.datetime.strptime(date, '%Y-%m-%d').date()
    elif isinstance(date, datetime.datetime):
        return date.date()
    elif isinstance(date, datetime.date):
        return date
    raise Exception("date 必须是datetime.date, datetime.datetime或者如下格式的字符串:'2015-01-05'")


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
    raise Exception("date 必须是datetime.date, datetime.datetime或者如下格式的字符串:'2015-01-05'")


def float_or_nan(s):
    try:
        return float(s)
    except Exception:
        return NaN


def date_range(start_date, end_date):
    start_date = convert_date(start_date)
    end_date = convert_date(end_date)
    delta = datetime.timedelta(days=1)
    yield start_date
    tomorrow = start_date + delta
    while tomorrow <= end_date:
        yield tomorrow
        tomorrow += delta


def filter_dict_values(d, fields):
    return [d.get(field) for field in fields]


def check_fields(keys, fields):
    for item in set(fields):
        if item not in keys:
            raise Exception("字段 {} 不在 {} 中".format(item, str(keys)))


def binary_search(lst, x):
    from bisect import bisect_left
    i = bisect_left(lst, x)
    if i != len(lst) and lst[i] == x:
        return i
    return None


