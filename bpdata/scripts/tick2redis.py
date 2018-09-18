#!/usr/bin/env python
# coding: utf-8
import gevent
from gevent import monkey
from bpdata.depth import (huobi_tick,
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

monkey.patch_all()


if __name__ == '__main__':
    #utils.setup_basic_logging(True)
    huobi_tick()
    # g0 = gevent.spawn(huobi_tick)
    # g1 = gevent.spawn(okex_tick)
    # g2 = gevent.spawn(binance_tick)
    # g3 = gevent.spawn(bitfinex_tick)
    # g4 = gevent.spawn(bibox_tick)
    # g5 = gevent.spawn(zb_tick)
    # g6 = gevent.spawn(bigone_tick)
    # g7 = gevent.spawn(kucoin_tick)
    # g8 = gevent.spawn(fcoin_tick)
    # g10 = gevent.spawn(otcbtc_tick)
    # g0.join()
    # g1.join()
    # g2.join()
    # g3.join()
    # g4.join()
    # g5.join()
    # g6.join()
    # g7.join()
    # g8.join()
    # g10.join()

    # g9 = gevent.spawn(binmex_tick)
