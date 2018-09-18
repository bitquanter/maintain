#!/usr/bin/env python
#-*- coding: utf-8 -*-
import datetime
import time
from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler
import redis
from bpdata.bp_db import DbUtil
from bpdata.exchange_coin import bp_coin_pair


db = DbUtil()
client = redis.StrictRedis.from_url('localhost:6379')


def get_redis_key():
    exchange_coins = []
    for ex in bp_coin_pair:
        for quote in bp_coin_pair[ex]:
            for base in bp_coin_pair[ex][quote]:
                ex_coin_str = 'tick/%s/%s%s'%(ex, base, quote)
                exchange_coins.append(ex_coin_str)
    return exchange_coins


redis_keys = get_redis_key()



def parse_data(data, exchange):
    pass



def job_func():
    now = datetime.now()
    cur_time = datetime(now.year, now.month, now.day, now.hour, now.minute, 0)
    update_data = []
    print(cur_time)
    for rk in redis_keys:
        raw_data = client.get(rk)
        if raw_data:
            item = {}
            item['time'] = cur_time
            item['name'] = rk.replace('tick/', '')
            item['data'] = raw_data
            # price, vol = parse_data(raw_data, rk.split('/')[1])
            # item['price'] = price
            # item['volume'] = vol
            update_data.append(item)
    db.update_fund_dynamic_data(update_data)
    pass


def main():
    '''
    每隔固定时间取redis中数据存到数据库
    '''
    scheduler = BackgroundScheduler()
    # 每隔五分钟执行一次 job_func 方法
    scheduler.add_job(job_func, 'interval', minutes=5, start_date='2018-08-31 00:00:00')
    scheduler.start()
    while True:
        time.sleep(5)



# Script starts from here
if __name__ == "__main__":
    main()
