#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function, unicode_literals
import time
import datetime
from exchange_coin import get_all_tick_keys, get_all_depth_keys
from redis_store import RedisStore
import json
import utils

store = RedisStore()

tick_keys = get_all_tick_keys()
depth_keys = get_all_depth_keys()
sta = {}
stac = {}
stac['time'] = []
for k in tick_keys:
    if k not in sta:
        sta[k] = {}
        sta[k]['exist'] = []
        sta[k]['lost'] = []
    if k not in stac:
        stac[k] = {}
        stac[k]['exist'] = 0
        stac[k]['lost'] = 0


def set_tick_expire():
    '''
    redis中所有tick关键字的数据设置超时时间1分钟
    '''
    for k in tick_keys:
        res = store.get(k)
        if res:
            store.expire(k, 60)
    pass


def check_tick_active():
    '''
    检查记录redis中某一时刻的tick数据活跃程度
    '''
    check = {}
    dt = datetime.datetime.now()
    check['time'] = dt.strftime('%Y-%m-%d_%H:%M:%S')
    check['active_count'] = 0
    check['active_coins'] = []
    check['lost_count'] = 0
    check['lost_coins'] = []
    for k in tick_keys:
        res = store.get(k)
        if res:
            check['active_count'] += 1
            check['active_coins'].append(k.replace('tick/',''))
        else:
            check['lost_count'] += 1
            check['lost_coins'].append(k.replace('tick/',''))
    store.set('check/tick_active', json.dumps(check))
    utils.record_tick_active(check)
    pass


def stat_tick_active():
    '''
    统计每个币对tick活跃时间，暂不写入redis
    '''
    dt = datetime.datetime.now()
    tim = dt.strftime('%Y-%m-%d %H:%M:%S')
    for k in tick_keys:
        res = store.get(k)
        if res:
            sta[k]['exist'].append(tim)
        else:
            sta[k]['lost'].append(tim)
    # store.set('stat/keys', json.dumps(sta))
    pass


def stat_tick_active_count():
    '''
    统计每个币对tick活跃次数，写入redis
    '''
    dt = datetime.datetime.now()
    stac['time'].append(dt.strftime('%Y-%m-%d %H:%M:%S'))
    for k in tick_keys:
        res = store.get(k)
        if res:
            stac[k]['exist'] += 1
        else:
            stac[k]['lost'] += 1
    store.set('stat/tick_active', json.dumps(stac))
    pass


def get_all_data():
    res = []
    for k in tick_keys:
        item = {}
        item['key'] = k
        item['value'] = store.get(k)
        dt = datetime.datetime.now()
        item['time']=dt
        res.append(item)
    return res 
    pass
