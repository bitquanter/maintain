#!/usr/bin/env python
# coding: utf-8
import gevent
from gevent import monkey
import utils
from redis_monitor import set_redis_expire, check_active_key_count, stat_key_active, stat_key_active_count

monkey.patch_all()


if __name__ == '__main__':
    utils.setup_basic_logging(True)
    sre = gevent.spawn(set_redis_expire)
    cc = gevent.spawn(check_active_key_count)
    stat = gevent.spawn(stat_key_active)
    stat_count = gevent.spawn(stat_key_active_count)
    sre.join()
    cc.join()
    stat.join()
    stat_count.join()
