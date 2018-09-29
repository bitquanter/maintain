# -*- coding: utf-8 -*-

from websocket import create_connection
import gzip
import time
import json
import datetime
import os
import pandas as pd
from os.path import join


coins = ['eth.usdt','bch.usdt','btc.usdt','eos.btc','eos.usdt','xrp.usdt','ltc.usdt','eth.btc','bch.btc','eos.eth']
period = '1min'
start_date = datetime.date(2018,1,1)
end_date = datetime.date(2018,9,20)

outputs = '/home/zhengdalong/data'
# file path format is ouputs/2018-09-11/1min/huobi/btc.usdt.csv

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


def id_sort(s):
    return s['id']

def get_all_days(start_date, end_date):
    count = (end_date - start_date).days
    all_days = [start_date + datetime.timedelta(days = i) for i in range(count + 1)]
    return all_days
    pass


def get_1min_klines(ws, begin, end, coin_pair):
    req = {}
    req['req'] = "market.%s.kline.1min"%(coin_pair)  
    req['id'] = 'id10'
    req['from'] = begin
    req['to'] = end
    # 请求 KLine 数据
    tradeStr=json.dumps(req)
    ws.send(tradeStr)
    while(1):
        compressData=ws.recv()
        result=gzip.decompress(compressData).decode('utf-8')
        if result[:7] == '{"ping"':
            ts=result[8:21]
            pong='{"pong":'+ts+'}'
            ws.send(pong)
            ws.send(tradeStr)
        else:
            res = json.loads(result)
            if 'data' in res:
                data = res['data']
                data = sorted(data, key=id_sort)
                return data
    pass


def get_someday_kline(ws, date, coin_pair):
    dt = to_timestamp(date)
    dt_list = [[dt+i*3600*4-60, dt+(i+1)*3600*4-60] for i in range(6)]
    res = []
    for tim in dt_list:
        kd = get_1min_klines(ws, tim[0], tim[1], coin_pair)
        res += kd
    return res
    pass



def get_klines():
    while(1):
        try:
            ws = create_connection("wss://api.huobipro.com/ws")
            break
        except:
            print('connect ws error,retry...')
            time.sleep(5)
    all_days = get_all_days(start_date, end_date)
    for day in all_days:
        for coin in coins:
            print(day, coin)
            spec_path = join(outputs,str(day),'1min','huobi')
            if not os.path.exists(spec_path):
                os.makedirs(spec_path)
            file_path = join(spec_path, '%s.csv'%(coin))
            if not os.path.exists(file_path):
                symbol = coin.replace('.','')
                res = get_someday_kline(ws, day, symbol)
                df = pd.DataFrame(res,columns=['id', 'open', 'close', 'low', 'high', 'amount', 'count', 'vol'])
                df.to_csv(file_path)
                time.sleep(0.5)
    return True


if __name__ == '__main__':
    while True:
        try:
            print('start req huobi kline')
            res = get_klines()
            if res:
                break
        except:
            print("huobi retry...")
