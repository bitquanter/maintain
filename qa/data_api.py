# -*- coding: utf-8 -*-
import os
from os.path import join
import pandas as pd
import datetime
import numpy as np

import sys
if sys.version_info[0] == 3:
    xrange = range


data_path = '/home/zhengdalong/data'

DEFAULE_FIELD = ['id','open', 'close', 'low', 'high', 'amount', 'count', 'vol']



def to_datetime(ts):
    return datetime.datetime.utcfromtimestamp(int(ts))


def group_array(a, group, field):
    if group > 1:
        new_int_index = xrange(0, len(a), group)
        grouper = {
            'open': (lambda v: [v[i] for i in new_int_index]),
            'close': (lambda v: [v[min(i+group, len(v)-1)] for i in new_int_index]),
            'high': (lambda v: [max(v[i:i+group]) for i in new_int_index]),
            'low': (lambda v: [min(v[i:i+group]) for i in new_int_index]),
            'vol': (lambda v: [sum(v[i:i+group]) for i in new_int_index]),
            'amount': (lambda v: [sum(v[i:i+group]) for i in new_int_index]),
            'count': (lambda v: [sum(v[i:i+group]) for i in new_int_index]),
            # same to close
            'id': (lambda v: [v[min(i+group, len(v)-1)] for i in new_int_index]),
        }
        a = grouper[field](a)
        if not isinstance(a, np.ndarray):
            a = np.array(a)
    return a


def get_price(security, start_date=None, end_date=None, frequency='1min', fields=None):
    '''
    获取标的行情数据    
    Args:
        security: 标的 huobi/btc.usdt 
        start_date: 开始日期 '2018-05-01'
        end_date: 结束日期 '2018-09-11'
        frequency: 周期
        fields: 字段 [open', 'close', 'low', 'high', 'amount', 'count', 'vol']
    Returns:
        pandas.DataFrame
    '''
    count = (end_date - start_date).days
    all_days = [start_date + datetime.timedelta(days = i) for i in range(count + 1)]
    exchange = security.split('/')[0]
    coins = security.split('/')[1]
    dfs = []
    for day in all_days:
        file_path = join(data_path, str(day), '1min', exchange,'%s.csv'%(coins))
        if not os.path.exists(file_path):
        	continue
        df = pd.read_csv(file_path)
        dfs.append(df)
    res = pd.concat(dfs)
    group = int(frequency.replace('min',''))
    dict_by_column = {f: group_array(list(res[f]), group, f) for f in DEFAULE_FIELD}
    res = pd.DataFrame(dict_by_column)
    res['id'] = pd.to_datetime(res['id'], unit='s')
    res = res.set_index(['id'])
    res = res.loc[:, list(fields)]
    return res
    pass



if __name__ == '__main__':
    df = get_price('huobi/btc.usdt',datetime.date(2018, 1, 1), datetime.date(2018, 1, 2), frequency='1min',fields=['close','vol'])
    print(df)
    df = get_price('huobi/btc.usdt',datetime.date(2018, 1, 1), datetime.date(2018, 1, 2), frequency='5min',fields=['close','vol'])
    print(df)
