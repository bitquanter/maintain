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
from binance.client import Client
from binance.depthcache import DepthCacheManager
# from binance.websockets import BinanceSocketManager
from config import get_config
from redis_store import RedisStore

client = Client('', '')

cfg = get_config()
log = logging.getLogger('bpdata')
store = RedisStore()

# _default_refresh = 30 * 60
# def bib_depth_cache_new(self, client, symbol, callback=None, refresh_interval=_default_refresh):
#     self._client = client
#     self._symbol = symbol
#     self._callback = callback
#     self._last_update_id = None
#     self._depth_message_buffer = []
#     self._bm = None
#     self._depth_cache = DepthCache(self._symbol)
#     self._refresh_interval = refresh_interval
#     print(symbol,callback)
#     pass


# DepthCacheManager.__init__ = bib_depth_cache_new


def huobi_depth():
    while True:
        try:
            print('start huobi depth')
            _huobi_depth()
        except:
            print("huobi retry...")


def _huobi_depth():
    # 连接火币行情
    ws = create_connection("wss://api.huobipro.com/ws")
    sym_dic = cfg.get_symbols('huobi')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = '%s%s'%(i,k)
            symbols.append(tradeStr)
    print(len(symbols))
    for s in symbols:
        item = {}
        item['sub'] = 'market.%s.depth.step0'%(s)
        item['id'] = cfg.get_id()
        sub_str = json.dumps(item)
        ws.send(sub_str)
    while(1):
        compressData=ws.recv()
        if not isinstance(compressData, bytes):
            print(type(compressData))
            break
        result=gzip.decompress(compressData).decode('utf-8')
        if result[:7] == '{"ping"':
            ts=result[8:21]
            pong='{"pong":'+ts+'}'
            ws.send(pong)
        else:
            res = json.loads(result)
            if 'tick' in res:
                coin_pair = res['ch'].strip().split('.')[1]
                key = 'depth/%s/%s'%('huobi',coin_pair)
                store.set(key, json.dumps(res))
    pass


def okex_depth():
    while True:
        try:
            print('start okex depth')
            _okex_depth()
        except:
            print('okex retry...')
    pass


def _okex_depth():
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
        item['channel'] = 'ok_sub_spot_%s_depth'%(symbol)
        sub_str = json.dumps(item)
        ws.send(sub_str)
    while(1):
        result=ws.recv()
        res = json.loads(result)[0]
        if 'data' in res and res['channel'] != 'addChannel':
            channel = res['channel'].strip().split('_')
            key = 'depth/%s/%s%s'%('okex',channel[3], channel[4])
            store.set(key, json.dumps(res))
    pass


def binance_depth():
    while True:
        try:
            print('start binance depth')
            _binance_depth_onetoken()
        except:
            print('binance retry...')
    pass


def _binance_depth():
    # 链接币安行情
    sym_dic = cfg.get_symbols('binance')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = '%s%s'%(i,k)
            symbols.append(tradeStr.upper())
    # bm = BinanceSocketManager(client)
    for sym in symbols:
        dcm = DepthCacheManager(client, sym, callback=_on_binance_depth)
    #     partial_key = bm.start_depth_socket('BNBBTC', binance_depth_callback, depth=BinanceSocketManager.WEBSOCKET_DEPTH_5)
    # bm.start()
    pass


def _on_binance_depth(data):
    # print('callback')
    # print(data)
    if data:
        key = 'tick/%s/%s'%('binance',data.symbol.lower())
        item = {}
        item['ask'] = data.get_asks()[:5] 
        item['bid'] = data.get_bids()[:5]
        item['timestamp'] = time.time()
        print(key)
        store.set(key, json.dumps(item))
    pass


def _binance_depth_onetoken():
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
            key = 'depth/%s'%(currency.replace('.',''))
            value = json.dumps(json_data['data'])
            store.set(key, value)
    pass


def bitfinex_depth():
    while True:
        try:
            print('start bitfinex depth')
            _bitfinex_depth()
        except:
            print('bitfinex retry...')


def _bitfinex_depth():
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
        item['channel'] = 'trades'
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
                key = 'depth/bitfinex/%s'%(id_map[ch_id].lower())
                store.set(key, result)
    pass


def bibox_depth():
    while True:
        try:
            print('start bibox depth')
            _bibox_depth()
        except:
            print('bibox retry...')


def _bibox_depth():
    sym_dic = cfg.get_symbols('bibox')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = '%s_%s'%(i, k)
            symbols.append(tradeStr.upper())
    while True:
        for sym in symbols:
            url = 'https://api.bibox.com/v1/mdata?cmd=depth&pair=%s&size=10'%(sym)
            response = requests.request("GET", url)
            #dep = json.loads(response.text)
            key = 'depth/%s/%s'%('bibox',sym.replace('_','').lower())
            store.set(key, response.text)
            time.sleep(0.2)
    pass


def zb_depth():
    while True:
        try:
            print('start zb depth')
            _zb_depth()
        except:
            print('zb retry...')


def _zb_depth():
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
        item['channel'] = '%s_depth'%(s)
        sub_str = json.dumps(item)
        ws.send(sub_str)
    while(1):
        result = ws.recv()
        res_json = json.loads(result)
        key = 'depth/zb/%s'%(res_json['channel'].split('_')[0])
        store.set(key, result)
    pass


def bigone_depth():
    while True:
        try:
            print('start bigone depth')
            _bigone_depth()
        except:
            print('bigone retry...')


def _bigone_depth():
    sym_dic = cfg.get_symbols('bigone')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = '%s-%s'%(i, k)
            symbols.append(tradeStr.upper())
    while True:
        for sym in symbols:
            url = 'https://big.one/api/v2/markets/%s/depth'%(sym)
            response = requests.request("GET", url)
            #dep = json.loads(response.text)
            key = 'depth/%s/%s'%('bigone',sym.replace('-','').lower())
            store.set(key, response.text)
            time.sleep(0.01)
    pass


def kucoin_depth():
    while True:
        try:
            print('start kucoin depth')
            _kucoin_depth()
        except:
            print('kucoin retry...')


def _kucoin_depth():
    sym_dic = cfg.get_symbols('kucoin')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = '%s-%s'%(i, k)
            symbols.append(tradeStr.upper())
    while True:
        for sym in symbols:
            url = 'https://api.kucoin.com/v1/%s/open/orders'%(sym)
            response = requests.request("GET", url)
            #dep = json.loads(response.text)
            key = 'depth/%s/%s'%('kucoin',sym.replace('-','').lower())
            store.set(key, response.text)
            time.sleep(0.01)
    pass


def fcoin_depth():
    while True:
        try:
            print('start fcoin depth')
            _fcoin_depth()
        except:
            print('fcoin retry...')


def _fcoin_depth():
    ws = create_connection("wss://api.fcoin.com/v2/ws")
    sym_dic = cfg.get_symbols('fcoin')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = 'depth.L20.%s%s'%(i,k)
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
        if 'depth' in json_res['type']:
            key = 'depth/fcoin/%s'%(json_res['type'].split('.')[2])
            store.set(key, result)
    pass


def binmex_depth():
    while True:
        try:
            print('start binmex depth')
            _binmex_depth()
        except:
            print('binmex retry...')


def _binmex_depth():
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


def _on_binmex(ws, msg):
    msg = json.loads(msg)
    print(msg)
    pass


def _binmex_depth_restful():
    sym_dic = cfg.get_symbols('binmex')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = '%s%s'%(i, k)
            symbols.append(tradeStr.upper())
    while True:
        for sym in symbols:
            url = 'https://www.bitmex.com/api/v1/orderBook/L2?symbol=%s&depth=25'%(sym)
            response = requests.request("GET", url)
            print(response.text)
    pass


def otcbtc_depth():
    while True:
        try:
            print('start otcbtc depth')
            _otcbtc_depth()
        except:
            print('otcbtc retry...')


def _otcbtc_depth():
    sym_dic = cfg.get_symbols('otcbtc')
    symbols = []
    for k in sym_dic:
        for i in sym_dic[k]:
            tradeStr = '%s%s'%(i, k)
            symbols.append(tradeStr)
    while True:
        for sym in symbols:
            url = 'https://bb.otcbtc.com/api/v2/depth?market=%s&limit=10'%(sym)
            response = requests.request("GET", url)
            #dep = json.loads(response.text)
            key = 'depth/%s/%s'%('otcbtc',sym)
            store.set(key, response.text)
            time.sleep(0.3)
    pass
