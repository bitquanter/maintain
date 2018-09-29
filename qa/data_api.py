# -*- coding: utf-8 -*-
import os
from os.path import join
import pandas as pd
import datetime



data_path = '/home/zhengdalong/data'


def get_price(security, start_date=None, end_date=None, frequency='1min', fields=None):
    '''
    获取标的行情数据    
    Args:
        security: 标的 huobi/btc.usdt 
        start_date: 开始日期 '2018-05-01'
        end_date: 结束日期 '2018-09-11'
        frequency: 周期
        fields: 字段 ['id', 'open', 'close', 'low', 'high', 'amount', 'count', 'vol']
    Returns:
        pandas.DataFrame
    '''
    count = (end_date - start_date).days
    all_days = [start_date + datetime.timedelta(days = i) for i in range(count + 1)]
    exchange = security.split('/')[0]
    coins = security.split('/')[1]
    dfs = []
    for day in all_days:
        file_path = join(data_path, str(day), frequency, exchange,'%s.csv'%(coins))
        if not os.path.exists(file_path):
        	continue
        df = pd.read_csv(file_path)
        dfs.append(df)
    res = pd.concat(dfs)
    res = res.set_index(['id'])
    res = res.loc[:, list(fields)]
    return res
    pass


if __name__ == '__main__':
	df = get_price('huobi/btc.usdt',datetime.date(2018, 5, 1), datetime.date(2018, 9, 11), frequency='kline',fields=['close','vol'])
	print(df)
