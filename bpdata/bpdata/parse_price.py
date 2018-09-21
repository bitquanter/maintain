# coding: utf-8
import json
import time

def parse_price(exchange, data):
    if exchange == 'huobi':
        return _parse_huobi(data)
    elif exchange == 'okex':
        return _parse_okex(data)
    elif exchange == 'binance':
        return _parse_binance(data)
    elif exchange == 'bitfinex':
        return _parse_bitfinex(data)
    elif exchange == 'bibox':
        return _parse_bibox(data)
    elif exchange == 'zb':
        return _parse_zb(data)
    elif exchange == 'bigone':
        return _parse_bigone(data)
    elif exchange == 'kucoin':
        return _parse_kucoin(data)
    elif exchange == 'fcoin':
        return  _parse_fcoin(data)
    elif exchange == 'binmex':
        return _parse_binmex(data)
    elif exchange == 'otcbtc':
        return _parse_otcbtc(data)
    elif exchange == '1token':
        return _parse_1token(data)
    else:
        pass
    pass


def _parse_huobi(data):
    res = {}
    if data and 'tick' in data:
        res['last_price'] = data['tick']['close']
        res['vol'] = data['tick']['vol']
        res['ts'] = time.time()
    return res
    pass


def _parse_okex(data):
    res = {}
    res['last_price'] = data['data']['last']
    res['vol'] = data['data']['vol']
    res['ts'] = time.time()
    return res
    pass


def _parse_binance(data):
    res = {}
    res['last_price'] = data['last']
    res['vol'] = data['volume']
    res['ts'] = time.time()
    return res
    pass


def _parse_bitfinex(data):
    res = {}
    if len(data) == 2:
        res['last_price'] = data[1][-4]
        res['vol'] = data[1][-3]
        res['ts'] = time.time()
    return res
    pass


def _parse_bibox(data):
    res = {}
    if data and 'result' in data:
        res['last_price'] = data['result']['last']
        res['vol'] = data['result']['vol']
        res['ts'] = time.time()
    return res
    pass


def _parse_zb(data):
    res = {}
    if data and 'ticker' in data:
        res['last_price'] = data['ticker']['last']
        res['vol'] = data['ticker']['vol']
        res['ts'] = time.time()
    return res
    pass


def _parse_bigone(data):
    res = {}
    if data and 'volume' in data:
        res['last_price'] = data['close']
        res['volume'] = data['volume']
        res['ts'] = time.time()
    return res
    pass


def _parse_kucoin(data):
    res = {}
    if data and 'data' in data:
        res['last_price'] = data['data']['lastDealPrice']
        res['vol'] = data['data']['volValue']
        res['ts'] = time.time()
    return res
    pass


def _parse_fcoin(data):
    res = {}
    if data and 'ticker' in data:
        res['last_price'] = data['ticker'][0]
        res['vol'] = data['ticker'][1]
        res['ts'] = time.time()
    return res
    pass


def _parse_binmex(data):
    res = {}
    if data:
        res['last_price'] = None
        res['vol'] = None
        res['ts'] = time.time()
    return res
    pass


def _parse_otcbtc(data):
    res = {}
    if data and 'ticker' in data:
        res['last_price'] = data['ticker']['last']
        res['vol'] = data['ticker']['vol']
        res['ts'] = time.time()
    return res
    pass


def _parse_1token(data):
    res = {}
    res['last_price'] = data['last']
    res['vol'] = data['volume']
    res['ts'] = time.time()
    return res
    pass
