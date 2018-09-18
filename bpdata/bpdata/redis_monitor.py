#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function, unicode_literals
import time
from exchange_coin import get_all_keys
from redis_store import RedisStore
import json

store = RedisStore()
keys = get_all_keys()

def set_redis_expire():
    while True:
        for k in keys:
            res = store.get(k)
            if res:
                store.expire(k, 60)
        time.sleep(60)
    pass


def check_active_key_count():
    while True:
        active_count = 0
        active_coins = []
        for k in keys:
            res = store.get(k)
            if res:
                active_count += 1
                active_coins.append(k)
        print("active key count:%s"%(active_count))
        #print(active_coins)
        time.sleep(120)
    pass


def stat_key_active():
    stat = {}
    for k in keys:
        if k not in stat:
            stat[k] = {}
            stat[k]['exist'] = []
            stat[k]['lost'] = []
    while True:
        tim = time.time()
        for k in keys:
            res = store.get(k)
            if res:
                stat[k]['exist'].append(tim)
            else:
                stat[k]['lost'].append(tim)
        store.set('stat/keys', json.dumps(stat))
        time.sleep(4 * 60)
    pass


def stat_key_active_count():
    stat = {}
    for k in keys:
        if k not in stat:
            stat[k] = {}
            stat[k]['exist'] = 0
            stat[k]['lost'] = 0
    while True:
        tim = time.time()
        for k in keys:
            res = store.get(k)
            if res:
                stat[k]['exist'] += 1
            else:
                stat[k]['lost'] += 1
        store.set('stat/keys_count', json.dumps(stat))
        time.sleep(4 * 60)
    pass