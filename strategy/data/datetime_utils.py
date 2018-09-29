#!/usr/bin/env python
#coding:utf-8

import datetime
import six
import numpy as np
from pandas import Timestamp


def get_all_days():
    start_date = datetime.datetime(2009, 1, 1)
    today = datetime.datetime.today()
    end_date = datetime.datetime(today.year, 12, 31)
    count = (end_date - start_date).days
    all_days = [start_date + datetime.timedelta(days = i) for i in range(count)]
    pass


def get_tss():
    all_days = get_all_days()
    dates = np.array([i.date() for i in all_days])
    dates.flags.writeable = False
    tss = vec2timestamp(dates)
    return tss
    pass

_coin_tss = get_tss()


def datetime_range(start_dt, end_dt, include_start=True, include_end=False):
    if not include_start:
        start_dt += datetime.timedelta(minutes=1)
    data = []
    while start_dt < end_dt:
        data.append(start_dt)
        start_dt += datetime.timedelta(minutes=1)
    if include_end:
        data.append(end_dt)
    return data


def parse_date(s):
    '''
    返回一个 datetime.date 对象
    '''
    # warning:
    # datetime.datetime isinstance of datetime.date
    if isinstance(s, datetime.datetime):
        return s.date()
    if isinstance(s, datetime.date):
        return s
    if isinstance(s, Timestamp):
        return s.date()
    if isinstance(s, six.string_types):
        if s.find("-") >= 0:
            if s.find(":") > 0:
                return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S").date()
            else:
                return datetime.datetime.strptime(s, "%Y-%m-%d").date()
        else:
            return datetime.datetime.strptime(s, "%Y%m%d").date()
    if isinstance(s, six.integer_types):
        return datetime.date(year=s//10000,
                             month=(s//100) % 100,
                             day=s%100)
    raise ValueError("Unknown {} for parse_date.".format(s))


def parse_datetime(s):
    if isinstance(s, datetime.datetime):
        return s
        # return s.replace(hour=0, minute=0, second=0, microsecond=0)
    if isinstance(s, datetime.date):
        return datetime.datetime.combine(s, datetime.time(0, 0))
    if isinstance(s, six.string_types):
        if s.find("-") >= 0:
            if s.find(":") > 0:
                return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
            else:
                return datetime.datetime.strptime(s, "%Y-%m-%d")
        else:
            return datetime.datetime.strptime(s, "%Y%m%d")
    if isinstance(s, six.integer_types):
        return datetime.datetime(year=s//10000,
                                 month=(s//100) % 100,
                                 day=s%100)
    raise ValueError("Unknown {} for parse_datetime.".format(s))


def to_timestamp(dt):
    '''
    将datetime或者date转换成时间戳。
    如果是 datetime, 忽略秒和微秒。
    如果是 date, 忽略小时，分钟，秒和微妙。
    '''
    if isinstance(dt, datetime.datetime):
        dt = dt.replace(second=0, microsecond=0)
        td = dt - datetime.datetime(1970,1,1)
    elif isinstance(dt, datetime.date):
        td = dt - datetime.date(1970,1,1)
    elif isinstance(dt, datetime.time):
        return dt.hour * 3600 + dt.minute * 60 + dt.second
    else:
        raise Exception("unkown dt=%s, type(dt) is %s" % (dt, type(dt)))
    return (td.seconds + td.days * 86400)


def to_datetime(ts):
    return datetime.datetime.utcfromtimestamp(int(ts))


def to_date(ts):
    return datetime.datetime.utcfromtimestamp(int(ts)).date()

def combine_time(d):
    return datetime.datetime.combine(d, datetime.datetime.min.time())

def trim_time(ts):
    '''
    去掉 timestamp 中的time部分，保证ts可以转化成一天。
    '''
    i = int(ts)
    return (i//86400) * 86400


def get_trade_days_by_enddt(end_date, start_date=None, count=None, include_now=True):
    '''
    返回时间戳
    '''
    assert start_date or count
    end_ts = to_timestamp(end_date)
    if not include_now:
        end_ts -= 86400 # 向前推移一天
    stop = np.searchsorted(_coin_tss, end_ts, 'right')
    if count:
        start = max(stop - count, 0)
    else:
        start = np.searchsorted(_coin_tss, to_timestamp(start_date))
    if stop > start:
        return _coin_tss[start:stop]
    return np.empty(0)


def get_trade_minutes_by_enddt(end_dt, start_dt=None, count=None, include_now=True):
    '''
    获取交易所的交易时间（分钟粒度）
    input: count
        返回 截止于 end_dt 的count个交易分钟。
    input：start_dt
        返回 start_dt 和 end_dt 之间的交易分钟列表，包括start_dt。
    include_now 表示返回结果是否包含 end_dt。
    '''
    assert start_dt or count
    end_ts = to_timestamp(end_dt)
    if not include_now:
        end_ts -= 60 # 向前推移1分钟
        end_dt = end_dt - datetime.timedelta(minutes=1)

    tss_table = _coin_tss
    trade_date = end_dt.date()
    stop = np.searchsorted(tss_table, to_timestamp(trade_date), 'right')
    if count:
        data = []
        i = stop - 1
        total_count = 0
        while i >= 0:
            minutes = vec2timestamp(datetime_range(to_datetime(tss_table[i]), to_datetime(tss_table[i + 1])))
            minutes = minutes[(minutes <= end_ts)]
            data.insert(0, minutes)
            total_count += len(minutes)
            i -= 1
            if total_count >= count:
                break
        data = np.concatenate(data)
        if len(data) > count:
            return data[-count:]
        return data
    else:
        start = np.searchsorted(tss_table, to_timestamp(start_dt.date()))
        if start >= stop:
            return []
        data = []
        for i in range(start, stop):
            minutes = vec2timestamp(datetime_range(to_datetime(tss_table[i]), to_datetime(tss_table[i + 1])))
            data.append(minutes)
        data = np.concatenate(data)
        return data[(data >= to_timestamp(start_dt)) & (data <= end_ts)]



vec2timestamp = np.vectorize(to_timestamp, otypes=[np.int])
vec2datetime = np.vectorize(to_datetime, otypes=[datetime.datetime])
vec2date = np.vectorize(to_date, otypes=[datetime.date])
vec2combine = np.vectorize(combine_time, otypes=[datetime.datetime])
vec2trimtime = np.vectorize(trim_time, otypes=[np.int])