#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function, unicode_literals
from websocket import create_connection
from btfxwss import BtfxWss
import sys,os
import gzip
import time
import logging
import json
import requests
import websocket
import threading
import urllib
import urllib.parse
import urllib.request
# from ref.bitmex_websocket import BitMEXWebsocket
from config import get_config
from redis_store import RedisStore
from parse_price import parse_price


cfg = get_config()
log = logging.getLogger('bpdata')
store = RedisStore()

def _http_get_request(url, params, add_to_headers=None):
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
    }
    if add_to_headers:
        headers.update(add_to_headers)
    postdata = urllib.parse.urlencode(params)
    response = requests.get(url, postdata, headers=headers, timeout=5) 
    try:
        
        if response.status_code == 200:
            return response.json()
        else:
            return
    except BaseException as e:
        print("httpGet failed, detail is:%s,%s" %(response.text,e))
        return

def huobi_tick():
    while True:
        try:
            print('start huobi tick')
            _huobi_tick()
        except:
            print("huobi retry...")


def _huobi_tick():
    # 连接火币行情
    sym_dic = cfg.get_symbols('huobi')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = '%s%s'%(i, k)
            symbols.append(tradeStr)
    while True:
        for symbol in symbols:
            params = {'symbol': symbol}
            url = 'https://api.huobi.pro/market/detail/merged'
            data = _http_get_request(url, params)
            res = parse_price('huobi',data)
            key = 'tick/huobi/%s'%(symbol)
            store.set(key, json.dumps(res))
            time.sleep(0.01)
    pass


def okex_tick():
    while True:
        try:
            print('start okex tick')
            _okex_tick()
        except:
            print('okex retry...')
    pass


def _okex_tick():
    # 链接 okex行情
    ws = create_connection("wss://real.okex.com:10441/websocket")
    sym_dic = cfg.get_symbols('okex')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = '%s_%s'%(i,k)
            symbols.append(tradeStr)
    print(len(symbols))
    for symbol in symbols:
        item = {}
        item['event'] = 'addChannel'
        item['channel'] = 'ok_sub_spot_%s_ticker'%(symbol)
        sub_str = json.dumps(item)
        ws.send(sub_str)
    while(1):
        result=ws.recv()
        res = json.loads(result)[0]
        if 'data' in res and res['channel'] != 'addChannel':
            channel = res['channel'].strip().split('_')
            key = 'tick/%s/%s%s'%('okex',channel[3], channel[4])
            res = parse_price('okex',res)
            store.set(key, json.dumps(res))
    pass


def binance_tick():
    while True:
        try:
            print('start binance tick')
            _binance_tick()
        except:
            print('binance retry...')
    pass



def _binance_tick():
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
            res = parse_price('binance', json_data['data'])
            store.set(key, json.dumps(res))
    pass


def bitfinex_tick():
    while True:
        try:
            print('start bitfinex tick')
            _bitfinex_tick()
        except:
            print('bitfinex retry...')


def _bitfinex_tick():
    # 连接bitfinex行情
    ws = create_connection("wss://api.bitfinex.com/ws/2")
    sym_dic = cfg.get_symbols('bitfinex')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = '%s%s'%(i,k)
            symbols.append(tradeStr.upper())
    print(len(symbols))
    for symbol in symbols:
        item = {}
        item['event'] = 'subscribe'
        item['channel'] = 'ticker'
        item['symbol'] = symbol
        sub_str = json.dumps(item)
        ws.send(sub_str)
    id_map = {}
    while(1):
        result=ws.recv()
        if 'event' in result:
            res = json.loads(result)
            if res['event'] == 'subscribed':
                id_map[res['chanId']] = res['pair']
        elif 'hb' not in result:
            res = json.loads(result)
            ch_id = res[0]
            if ch_id in id_map:
                key = 'tick/bitfinex/%s'%(id_map[ch_id].lower())
                res = parse_price('bitfinex', res)
                store.set(key, json.dumps(res))
    pass


def bibox_tick():
    while True:
        try:
            print('start bibox tick')
            _bibox_tick()
        except:
            print('bibox retry...')


def _bibox_tick():
    sym_dic = cfg.get_symbols('bibox')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = '%s_%s'%(i, k)
            symbols.append(tradeStr.upper())
    while True:
        for sym in symbols:
            url = 'https://api.bibox.com/v1/mdata?cmd=ticker&pair=%s'%(sym)
            response = requests.request("GET", url)
            res = json.loads(response.text)
            #dep = json.loads(response.text)
            key = 'tick/%s/%s'%('bibox',sym.replace('_','').lower())
            res = parse_price('bibox', res)
            store.set(key, json.dumps(res))
            time.sleep(0.2)
    pass


def zb_tick():
    while True:
        try:
            print('start zb tick')
            _zb_tick()
        except:
            print('zb retry...')


def _zb_tick():
    # 连接zb行情
    ws = create_connection("wss://api.zb.cn:9999/websocket")
    sym_dic = cfg.get_symbols('zb')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = '%s%s'%(i,k)
            symbols.append(tradeStr)
    for s in symbols:
        item = {}
        item['event'] = 'addChannel'
        item['channel'] = '%s_ticker'%(s)
        sub_str = json.dumps(item)
        ws.send(sub_str)
    while(1):
        result = ws.recv()
        res_json = json.loads(result)
        key = 'tick/zb/%s'%(res_json['channel'].split('_')[0])
        res = parse_price('zb', res_json)
        store.set(key, json.dumps(res))
    pass


def bigone_tick():
    while True:
        try:
            print('start bigone tick')
            _bigone_tick()
        except:
            print('bigone retry...')


def _bigone_tick():
    while True:
        url = 'https://big.one/api/v2/tickers'
        response = requests.request("GET", url)
        if 'html' not in response.text:
            res_json = json.loads(response.text)
            for r in res_json:
                key = 'tick/bigone/%s'%(r['market_id'].replace('-','').lower())
                res = parse_price('bigone', r)
                store.set(key, json.dumps(res))
            time.sleep(0.5)
        else:
            return
    pass


# def _bigone_tick():
#     sym_dic = cfg.get_symbols('bigone')
#     symbols = []
#     for k in sym_dic:
#         for i in sym_dic[k]:
#             tradeStr = '%s-%s'%(i, k)
#             symbols.append(tradeStr.upper())
#     while True:
#         for sym in symbols:
#             url = 'https://big.one/api/v2/markets/%s/ticker'%(sym)
#             response = requests.request("GET", url)
#             res = json.loads(response.text)
#             print(res)
#             #key = 'price/%s/%s'%('bigone',sym.replace('-','').lower())
#             #store.set(key, response.text)
#             time.sleep(0.01)
#     pass


def kucoin_tick():
    while True:
        try:
            print('start kucoin tick')
            _kucoin_tick()
        except:
            print('kucoin retry...')


def _kucoin_tick():
    sym_dic = cfg.get_symbols('kucoin')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = '%s-%s'%(i, k)
            symbols.append(tradeStr.upper())
    while True:
        for sym in symbols:
            url = 'https://api.kucoin.com/v1/%s/open/tick'%(sym)
            response = requests.request("GET", url)
            tick_data = json.loads(response.text)
            key = 'tick/kucoin/%s'%(sym.replace('-','').lower())
            res = parse_price('kucoin',tick_data)
            store.set(key, json.dumps(res))
            time.sleep(0.05)
    pass


# def _kucoin_tick():
#     ws = create_connection("wss://push1.kucoin.com/endpoint")
#     sym_dic = cfg.get_symbols('kucoin')
#     symbols = []
#     for k in sym_dic:
#         for i in sym_dic[k]:
#             tradeStr = '%s-%s'%(i,k)
#             symbols.append(tradeStr.upper())
#     for sym in symbols:
#         item = {}
#         item['id'] = 123
#         item['type'] = 'subscribe'
#         item['topic'] = '/market/%s_TICK'%(sym)
#         item['req'] = 1
#         sub_str = json.dumps(item)
#         ws.send(sub_str)
#     while(1):
#         result=ws.recv()
#         print(result)
#         #json_res = json.loads(result)
#     pass


def fcoin_tick():
    while True:
        try:
            print('start fcoin tick')
            _fcoin_tick()
        except:
            print('fcoin retry...')


def _fcoin_tick():
    ws = create_connection("wss://api.fcoin.com/v2/ws")
    sym_dic = cfg.get_symbols('fcoin')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = 'ticker.%s%s'%(i,k)
            symbols.append(tradeStr)
    item = {}
    item['cmd'] = 'sub'
    item['id'] = '2'
    item['args'] = symbols
    sub_str = json.dumps(item)
    ws.send(sub_str)
    while(1):
        result=ws.recv()
        json_res = json.loads(result)
        if 'ticker' in json_res:
            key = 'tick/fcoin/%s'%(json_res['type'].split('.')[1])
            res = parse_price('fcoin', json_res)
            store.set(key, json.dumps(res))
    pass


def binmex_tick():
    while True:
        try:
            print('start binmex tick')
            _binmex_tick()
        except:
            print('binmex retry...')


def _binmex_tick():
    # 链接 binmex ws
    #ws = create_connection("wss://www.bitmex.com/realtime")
    sym_dic = cfg.get_symbols('binmex')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = '%s%s'%(i,k)
            symbols.append(tradeStr.upper())
    print(len(symbols))
    for symbol in symbols:
        subscriptions = "orderBookL2:" + symbol.upper()
        url = 'wss://www.bitmex.com/realtime?subscribe={}'.format(subscriptions)
        ws = websocket.WebSocketApp(url, on_message=_on_binmex)
        wst = threading.Thread(target=lambda: ws.run_forever())
        wst.daemon = True
        wst.start()
        conn_timeout = 5
        while not ws.sock or not ws.sock.connected and conn_timeout:
            time.sleep(1)
            conn_timeout -= 1
        if not conn_timeout:
            ws.close()
    while True:
        time.sleep(0.1)
    pass


# def _on_binmex(ws, msg):
#     msg = json.loads(msg)
#     print(msg)
#     pass


def _binmex_restful():
    sym_dic = cfg.get_symbols('binmex')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = '%s%s'%(i, k)
            symbols.append(tradeStr.upper())
    while True:
        for sym in symbols:
            url = 'https://www.bitmex.com/api/v1/orderBook/L2?symbol=%s&tick=25'%(sym)
            response = requests.request("GET", url)
            print(response.text)
            print('=======================')
    pass


def otcbtc_tick():
    while True:
        try:
            print('start otcbtc tick')
            _otcbtc_tick()
        except:
            print('otcbtc retry...')


# def _otcbtc_tick():
#     sym_dic = cfg.get_symbols('otcbtc')
#     symbols = []
#     for k in sym_dic:
#         for i in sym_dic[k]:
#             tradeStr = '%s%s'%(i, k)
#             symbols.append(tradeStr)
#     while True:
#         for sym in symbols:
#             url = 'https://bb.otcbtc.com/api/v2/tick?market=%s&limit=10'%(sym)
#             response = requests.request("GET", url)
#             #dep = json.loads(response.text)
#             key = 'tick/%s/%s'%('otcbtc',sym)
#             store.set(key, response.text)
#             time.sleep(0.3)
#     pass


def _otcbtc_tick():
    while True:
        url = 'https://bb.otcbtc.com/api/v2/tickers'
        response = requests.request("GET", url)
        data = json.loads(response.text)
        for d in data:
            key = 'tick/otcbtc/%s'%(d.replace('_',''))
            res = parse_price('otcbtc',data[d])
            store.set(key, json.dumps(res))
        time.sleep(1)
    pass

