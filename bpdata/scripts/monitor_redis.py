#!/usr/bin/env python
# coding: utf-8
import gevent
from gevent import monkey
import bpdata.utils
from bpdata.redis_monitor import set_redis_expire, check_active_key_count

monkey.patch_all()


if __name__ == '__main__':
    utils.setup_basic_logging(True)
    sre = gevent.spawn(set_redis_expire)
    cc = gevent.spawn(check_active_key_count)
    sre.join()
    cc.join()
