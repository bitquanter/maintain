#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function, unicode_literals
from websocket import create_connection
import logging
import json
from config import get_config
from redis_store import RedisStore
from parse_price import parse_price


cfg = get_config()
log = logging.getLogger('bpdata')
store = RedisStore()


def binance_tick_1token():
    while True:
        try:
            print('start 1token binance tick')
            _binance_tick_1token()
        except:
            print('1token binance retry...')
    pass


def _binance_tick_1token():
    currency_list = []
    sym_dic = cfg.get_symbols('binance')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = 'binance/%s.%s'%(i,k)
            currency_list.append(tradeStr)
    ws = create_connection("wss://1token.trade/api/v1/ws/tick")
    auth_data = {"uri": "auth"}
    ws.send(json.dumps(auth_data))
    for cur in currency_list:
        request_data = {"uri": "subscribe-single-tick-verbose", "contract": cur}
        ws.send(json.dumps(request_data))
    while True:
        data = ws.recv()
        json_data = json.loads(data)
        if 'data' in json_data:
            currency = json_data['data']['contract']
            key = 'tick/%s'%(currency.replace('.',''))
            res = parse_price('1token', json_data['data'])
            store.set(key, json.dumps(res))
    pass


def zb_tick_1token():
    while True:
        try:
            print('start 1token zb tick')
            _zb_tick_1token()
        except:
            print('1token zb retry...')
    pass


def _zb_tick_1token():
    currency_list = []
    sym_dic = cfg.get_symbols('zb')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = 'zb/%s.%s'%(i,k)
            currency_list.append(tradeStr)
    ws = create_connection("wss://1token.trade/api/v1/ws/tick")
    auth_data = {"uri": "auth"}
    ws.send(json.dumps(auth_data))
    for cur in currency_list:
        request_data = {"uri": "subscribe-single-tick-verbose", "contract": cur}
        ws.send(json.dumps(request_data))
    while True:
        data = ws.recv()
        json_data = json.loads(data)
        if 'data' in json_data:
            currency = json_data['data']['contract']
            key = 'tick/%s'%(currency.replace('.',''))
            res = parse_price('1token', json_data['data'])
            print(key,res)
            #store.set(key, json.dumps(res))
    pass


def bitfinex_tick_1token():
    while True:
        try:
            print('start 1token bitfinex tick')
            _bitfinex_tick_1token()
        except:
            print('1token bitfinex retry...')
    pass
    pass


def _bitfinex_tick_1token():
    currency_list = []
    sym_dic = cfg.get_symbols('bitfinex')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = 'bitfinex/%s.%s'%(i,k)
            currency_list.append(tradeStr)
    ws = create_connection("wss://1token.trade/api/v1/ws/tick")
    auth_data = {"uri": "auth"}
    ws.send(json.dumps(auth_data))
    for cur in currency_list:
        request_data = {"uri": "subscribe-single-tick-verbose", "contract": cur}
        ws.send(json.dumps(request_data))
    while True:
        data = ws.recv()
        json_data = json.loads(data)
        if 'data' in json_data:
            currency = json_data['data']['contract']
            key = 'tick/%s'%(currency.replace('.',''))
            res = parse_price('1token', json_data['data'])
            print(key,res)
            #store.set(key, json.dumps(res))
    pass


def bitflyer_tick_1token():
    pass


def _bitflyer_tick_1token():
    pass


def bithumb_tick_1token():
    pass


def _bithumb_tick_1token():
    pass


def bitmex_tick_1token():
    pass


def _bitmex_tick_1token():
    pass


def bittrex_tick_1token():
    pass


def _bittrex_tick_1token():
    pass


def gate_tick_1token():
    pass


def _gate_tick_1token():
    pass


def huobi_tick_1token():
    pass


def _huobi_tick_1token():
    pass


def hadax_tick_1token():
    pass


def _hadax_tick_1token():
    pass


def okex_tick_1token():
    pass


def _okex_tick_1token():
    pass


def okef_tick_1token():
    pass


def _okef_tick_1token():
    pass


def poloniex_tick_1token():
    pass


def _poloniex_tick_1token():
    pass


def quoinex_tick_1token():
    pass


def _quoinex_tick_1token():
    pass
