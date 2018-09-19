#!/usr/bin/env python
# coding: utf-8
import time
from apscheduler.schedulers.background import BackgroundScheduler
import utils
from redis_monitor import set_tick_expire, check_tick_active, stat_tick_active, stat_tick_active_count


if __name__ == '__main__':
    '''
    监控redis数据
    '''
    utils.setup_basic_logging(True)
    scheduler = BackgroundScheduler()
    # 每隔1分钟执行一次 set_tick_expire 方法
    scheduler.add_job(set_tick_expire, 'interval', minutes=1, start_date='2018-09-19 00:00:00')
    # 每隔4分钟执行一次 check_tick_active 方法
    scheduler.add_job(check_tick_active, 'interval', minutes=4, start_date='2018-09-19 00:00:00')
    # 每隔4分钟执行一次 stat_tick_active 方法
    scheduler.add_job(stat_tick_active, 'interval', minutes=4, start_date='2018-09-19 00:00:00')
    # 每隔4分钟执行一次 stat_tick_active_count 方法
    scheduler.add_job(stat_tick_active_count, 'interval', minutes=4, start_date='2018-09-19 00:00:00')
    scheduler.start()
    while True:
        time.sleep(5)
