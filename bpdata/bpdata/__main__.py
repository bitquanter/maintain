#!/usr/bin/env python
# coding: utf-8
import gevent
from gevent import monkey
import utils
from depth import (huobi_depth,
    okex_depth,
    binance_depth,
    bitfinex_depth,
    bibox_depth,
    zb_depth,
    bigone_depth,
    kucoin_depth,
    fcoin_depth,
    binmex_depth,
    otcbtc_depth,)
from redis_monitor import set_redis_expire, check_active_key_count

monkey.patch_all()


if __name__ == '__main__':
    utils.setup_basic_logging(True)
    g0 = gevent.spawn(huobi_depth)
    g1 = gevent.spawn(okex_depth)
    g2 = gevent.spawn(binance_depth)
    g3 = gevent.spawn(bitfinex_depth)
    g4 = gevent.spawn(bibox_depth)
    g5 = gevent.spawn(zb_depth)
    g6 = gevent.spawn(bigone_depth)
    g7 = gevent.spawn(kucoin_depth)
    g8 = gevent.spawn(fcoin_depth)
    g10 = gevent.spawn(otcbtc_depth)
    sre = gevent.spawn(set_redis_expire)
    cc = gevent.spawn(check_active_key_count)
    g0.join()
    g1.join()
    g2.join()
    g3.join()
    g4.join()
    g5.join()
    g6.join()
    g7.join()
    g8.join()
    g10.join()
    sre.join()
    cc.join()

    # g9 = gevent.spawn(binmex_depth)
