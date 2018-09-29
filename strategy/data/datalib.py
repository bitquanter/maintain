#!/usr/bin/env python
#coding:utf-8

'''
取bcolz数据相关接口
'''
import sys
if sys.version_info[0] == 3:
    xrange = range
    
import math
import datetime
import numpy as np

from .datetime_utils import to_timestamp, to_datetime, get_trade_days_by_enddt, get_trade_minutes_by_enddt
from .bar_port import (get_minute_bar_by_count,
    get_minute_bar_by_period,
    get_daily_bar_by_count,
    get_daily_bar_by_period,
    get_date_by_count,
    get_date_by_period,
    get_minute_by_count,
    get_minute_by_period,)


__all__ = [
    'get_price_daily_single',
    'get_price_minute_single',
]

nan = float('nan')

EMPTY_ARRAY = np.empty((0,))

def paused_day_array(cols):
    arr = []
    for col in cols:
        if col in ['open', 'close', 'high', 'low']:
            arr.append(0.0)
        elif col in ['volume', 'money']:
            arr.append(0.0)
    return np.array(arr, dtype=float)


def fill_paused(security, cols_dict, index, full_index, fields, index_type='date'):
    '''
    index 是 a的索引
    full_index 是完整的交易索引。

    index_type 表示 dates 和 trade_dates的类型， 'date' 表示日期， 'minute' 表示 分钟
    '''
    # 获取最大有效数据日期, 超过此日期数据为nan
    if index_type == 'minute':
        max_valid_date = datetime.datetime.now().replace(second=0, microsecond=0)
    elif index_type == 'date':
        max_valid_date = datetime.date.today()
    else:
        raise Exception("wrong index_type=%s, should be 'date' or 'minute'" % index_type)
    max_valid_ts = to_timestamp(max_valid_date)
    v = np.searchsorted(index, full_index, 'right') - 1
    a = np.column_stack((cols_dict[f] for f in fields))
    nan_const = np.full(a.shape[1], nan)
    b = []
    for i, vi in enumerate(v):
        if vi < 0:
            b.append(nan_const) # 未上市
        else:
            index_ts = index[vi]
            full_index_ts = full_index[i]
            if full_index_ts != index_ts:
                if full_index_ts > max_valid_ts:
                    b.append(nan_const)
                else:
                    b.append(paused_day_array(fields))
            else:
                b.append(a[vi])
    new_a = np.array(b).reshape(len(b), a.shape[1])
    for i, col in enumerate(fields):
        cols_dict[col] = new_a[:,i]
    return cols_dict


def fetch_daily_data(security, end_date, fields, start_date=None, count=None, include_now=True):
    # 需要返回的行数
    return_count = None
    valid_trade_days = get_trade_days_by_enddt(end_date, start_date=start_date, count=count, include_now=include_now)
    if count:
        # assert len(valid_trade_days) <= count
        return_count = count
    else:
        return_count = len(valid_trade_days)
    if return_count <= 0:
        cols_dict = {col:EMPTY_ARRAY for col in fields}
        return cols_dict, EMPTY_ARRAY
    max_count = len(valid_trade_days) + 1
    cols_dict = get_daily_bar_by_count(security, end_date, max_count, fields, include_now=include_now)
    dates = cols_dict.pop('date', [])
    if len(dates) == 0:
        cols_dict = {col:np.full(len(valid_trade_days), nan) for col in fields}
        return cols_dict, valid_trade_days
    mask = np.in1d(valid_trade_days, dates, assume_unique=True)
    # 发生了停牌
    if not np.all(mask):
        cols_dict = fill_paused(security, cols_dict, dates, valid_trade_days, fields)
        dates = valid_trade_days
    else:
        start = np.searchsorted(dates, valid_trade_days[0])
        if start > 0:
            dates = dates[start:]
            for col in cols_dict:
                cols_dict[col] = cols_dict[col][start:]
    return cols_dict, dates


def calc_daily_indexs(security, end_date, start_date=None, count=None, include_now=True):
    '''
    计算日期索引
    '''
    dates = get_trade_days_by_enddt(end_date, start_date=start_date, count=count)
    if count and len(dates) < count:
        miss = count - len(dates)
        if len(dates) > 0:
            miss_end_date = dates[0]
        else:
            miss_end_date = to_timestamp(end_date)
        prev_dates = [(miss_end_date - i * 86400) for i in xrange(miss, 0, -1)]
        dates = np.concatenate((prev_dates, dates))
        return dates
    else:
        return dates


def fetch_minute_data(security, end_dt, fields, start_dt=None, count=None, include_now=True):
    # 需要返回的行数
    return_count = 0
    valid_trade_minutes = get_trade_minutes_by_enddt(end_dt, start_dt=start_dt, count=count, include_now=include_now)
    if count:
        # assert len(valid_trade_minutes) == count
        return_count = count
    else:
        return_count = len(valid_trade_minutes)

    if return_count <= 0:
        cols_dict = {col:EMPTY_ARRAY for col in fields}
        return cols_dict, EMPTY_ARRAY
    cols_dict = get_minute_bar_by_count(security, end_dt, return_count + 1, fields, include_now=include_now)
    minutes = cols_dict.pop('date', EMPTY_ARRAY)
    if len(minutes) == 0:
        cols_dict = {col:np.full(return_count, nan) for col in fields}
        return cols_dict, valid_trade_minutes

    mask = np.in1d(valid_trade_minutes, minutes, assume_unique=True)
    if not np.all(mask):
        cols_dict = fill_paused(security, cols_dict, minutes, valid_trade_minutes, fields)
        minutes = valid_trade_minutes
    else:
        start = np.searchsorted(minutes, valid_trade_minutes[0])
        if start > 0:
            minutes = minutes[start:]
            for col in cols_dict:
                cols_dict[col] = cols_dict[col][start:]

    return cols_dict, minutes


def calc_minute_indexs(security, end_dt, start_dt=None, count=None, include_now=True):
    '''
    计算分钟索引: 返回 numpy.ndarray, 每一项为时间戳
    '''
    minutes = get_trade_minutes_by_enddt(end_dt, start_dt=start_dt, count=count, include_now=include_now)
    if count and len(minutes) < count:
        miss = count - len(minutes)
        if len(minutes) > 0:
            miss_timestamp = minutes[0]
        else:
            miss_timestamp = to_timestamp(end_dt)
        prev_minutes = [(miss_timestamp - i*60) for i in xrange(miss, 0, -1)]
        minutes = np.concatenate((prev_minutes, minutes))
        return minutes
    else:
        return minutes


# 取天数据的核心函数, 取单只标的的天数据
def get_price_daily_single(security, end_date=None, fields=None, start_date=None, count=None, include_now=True):
    fields = list(set(fields))  # 去掉重复的列
    if not count:
        assert start_date is not None

    cols_dict, dates = fetch_daily_data(security, end_date, fields, start_date=start_date, count=count, include_now=include_now)
    price_decimals = 8
    for f in fields:
        if f in ['open', 'close', 'high', 'low']:
            np.round(cols_dict[f], price_decimals, cols_dict[f])
        elif f in ['volume']:
            np.round(cols_dict[f], 0, cols_dict[f])
    # 需要返回的行数
    return_dates = calc_daily_indexs(security, end_date, start_date=start_date, count=count, include_now=include_now)
    return_count = len(return_dates)
    if len(dates) < return_count:
        # pad nan
        miss = return_count - len(dates)
        prev = np.full(miss, nan)
        for f in fields:
            cols_dict[f] = np.concatenate((prev, cols_dict[f]))
        if len(dates) > 0:
            miss_date_timestamp = dates[0]
        else:
            miss_date_timestamp = to_timestamp(end_date)
        prev_dates = [(miss_date_timestamp - i*86400) for i in xrange(miss, 0, -1)]
        dates = np.concatenate((prev_dates, dates))

    return cols_dict, dates

def get_price_minute_single(security, end_dt=None, fields=None, start_dt=None, count=None, include_now=True, pre_factor_ref_date=None):
    fields = list(fields)
    fields = list(set(fields))  # 去掉重复的列
    minute_a, minute_index = fetch_minute_data(security, end_dt, fields, start_dt=start_dt, count=count, include_now=include_now)
    # minute_index = calc_minute_indexs(security, end_dt, start_dt=start_dt, count=count, include_now=include_now)

    if len(minute_index) == 0:
        cols_dict = {col:EMPTY_ARRAY for col in fields}
        return cols_dict, EMPTY_ARRAY
    else:
        cols_dict = minute_a

    price_decimals = 8
    for f in cols_dict.keys():
        if f in ['open', 'close', 'high', 'low']:
            np.round(cols_dict[f], price_decimals, cols_dict[f])
        elif f in ['volume']:
            np.round(cols_dict[f], 0, cols_dict[f])
    return cols_dict, minute_index
