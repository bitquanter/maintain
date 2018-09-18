#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function, unicode_literals
import time
from exchange_coin import get_all_keys
from redis_store import RedisStore

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
        print(active_coins)
        time.sleep(120)
    pass
