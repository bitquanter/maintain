#!/usr/bin/env python
# coding: utf-8
import gevent
from gevent import monkey
from tick import (huobi_tick,
    okex_tick,
    binance_tick,
    bitfinex_tick,
    bibox_tick,
    zb_tick,
    bigone_tick,
    kucoin_tick,
    fcoin_tick,
    binmex_tick,
    otcbtc_tick,)

import utils

monkey.patch_all()


if __name__ == '__main__':
    utils.setup_basic_logging(True)
    g0 = gevent.spawn(huobi_tick)  # websocket
    g1 = gevent.spawn(okex_tick)  # websocket
    g2 = gevent.spawn(binance_tick)  # websocket-1token
    g3 = gevent.spawn(bitfinex_tick)  # websocket
    g4 = gevent.spawn(bibox_tick)  # restful
    g5 = gevent.spawn(zb_tick)  # websocket
    g6 = gevent.spawn(bigone_tick)  # restful
    g7 = gevent.spawn(kucoin_tick)  # restful
    g8 = gevent.spawn(fcoin_tick)  # websocket
    g9 = gevent.spawn(binmex_tick)  # websocket
    g10 = gevent.spawn(otcbtc_tick) # restful
    g0.join()
    g1.join()
    g2.join()
    g3.join()
    g4.join()
    g5.join()
    g6.join()
    g7.join()
    g8.join()
    g9.join()
    g10.join()
