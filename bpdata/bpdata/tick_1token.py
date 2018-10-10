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
    while True:
        try:
            print('start 1token bitflyer tick')
            _bitflyer_tick_1token()
        except:
            print('1token bitflyer retry...')
    pass


def _bitflyer_tick_1token():
    currency_list = []
    sym_dic = cfg.get_symbols('bitflyer')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = 'bitflyer/%s.%s'%(i,k)
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


def bithumb_tick_1token():
    while True:
        try:
            print('start 1token bithumb tick')
            _bithumb_tick_1token()
        except:
            print('1token bithumb retry...')
    pass


def _bithumb_tick_1token():
    currency_list = []
    sym_dic = cfg.get_symbols('bithumb')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = 'bithumb/%s.%s'%(i,k)
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


def bitmex_tick_1token():
    while True:
        try:
            print('start 1token bitmex tick')
            _bitmex_tick_1token()
        except:
            print('1token bitmex retry...')
    pass


def _bitmex_tick_1token():
    currency_list = []
    sym_dic = cfg.get_symbols('bitmex')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = 'bitmex/%s.%s'%(i,k)
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


def bittrex_tick_1token():
    while True:
        try:
            print('start 1token bittrex tick')
            _bittrex_tick_1token()
        except:
            print('1token bittrex retry...')
    pass


def _bittrex_tick_1token():
    currency_list = []
    sym_dic = cfg.get_symbols('bittrex')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = 'bittrex/%s.%s'%(i,k)
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


def gate_tick_1token():
    while True:
        try:
            print('start 1token gate tick')
            _gate_tick_1token()
        except:
            print('1token gate retry...')
    pass


def _gate_tick_1token():
    currency_list = []
    sym_dic = cfg.get_symbols('gate')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = 'gate/%s.%s'%(i,k)
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


def huobi_tick_1token():
    while True:
        try:
            print('start 1token huobi tick')
            _huobi_tick_1token()
        except:
            print('1token huobi retry...')
    pass


def _huobi_tick_1token():
    currency_list = []
    sym_dic = cfg.get_symbols('huobi')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = 'huobi/%s.%s'%(i,k)
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


def hadax_tick_1token():
    while True:
        try:
            print('start 1token hadax tick')
            _hadax_tick_1token()
        except:
            print('1token hadax retry...')
    pass


def _hadax_tick_1token():
    currency_list = []
    sym_dic = cfg.get_symbols('hadax')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = 'hadax/%s.%s'%(i,k)
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


def okex_tick_1token():
    while True:
        try:
            print('start 1token okex tick')
            _okex_tick_1token()
        except:
            print('1token okex retry...')
    pass


def _okex_tick_1token():
    currency_list = []
    sym_dic = cfg.get_symbols('okex')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = 'okex/%s.%s'%(i,k)
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


def okef_tick_1token():
    while True:
        try:
            print('start 1token okef tick')
            _okef_tick_1token()
        except:
            print('1token okef retry...')
    pass


def _okef_tick_1token():
    currency_list = []
    sym_dic = cfg.get_symbols('okef')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = 'okef/%s.%s'%(i,k)
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


def poloniex_tick_1token():
    while True:
        try:
            print('start 1token poloniex tick')
            _poloniex_tick_1token()
        except:
            print('1token poloniex retry...')
    pass


def _poloniex_tick_1token():
    currency_list = []
    sym_dic = cfg.get_symbols('poloniex')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = 'poloniex/%s.%s'%(i,k)
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


def quoinex_tick_1token():
    while True:
        try:
            print('start 1token quoinex tick')
            _quoinex_tick_1token()
        except:
            print('1token quoinex retry...')
    pass


def _quoinex_tick_1token():
    currency_list = []
    sym_dic = cfg.get_symbols('quoinex')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = 'quoinex/%s.%s'%(i,k)
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
