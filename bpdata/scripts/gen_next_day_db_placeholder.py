#!/usr/bin/env python
#-*- coding: utf-8 -*-
import datetime
import time
from apscheduler.schedulers.background import BackgroundScheduler
from bpdata.bp_db import DbUtil
from bpdata.exchange_coin import bp_coin_pair

db = DbUtil()


def get_datetime_list(date, time_delta):
    time_list = []
    cur_time = datetime.datetime(date.year,date.month,date.day,0,0,0)
    while (cur_time.date() == date):
        time_list.append(cur_time)
        cur_time = cur_time + datetime.timedelta(seconds = time_delta*60)
    return time_list
    pass


def main():
    '''
    生成第二天币对-交易所-时间 空白数据
    '''
    # 获得币对交易所集合
    exchange_coins = []
    for ex in bp_coin_pair:
        for quote in bp_coin_pair[ex]:
            for base in bp_coin_pair[ex][quote]:
                ex_coin_str = '%s/%s%s'%(ex, base, quote)
                exchange_coins.append(ex_coin_str)
    # 获取每日五分钟时间间隔
    base_date = datetime.date.today() + datetime.timedelta(days=1)
    time_list = get_datetime_list(base_date, 5)
    db.gen_next_day_placeholder(exchange_coins,time_list)
    pass
    


# Script starts from here
if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    main()
    scheduler.add_job(main, 'interval', days=1, start_date='2018-08-31 23:00:00')
    scheduler.start()
    while True:
        time.sleep(5)
