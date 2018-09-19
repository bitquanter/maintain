#!/usr/bin/env python
# coding: utf-8
import json
import pickle
import os
import time
import requests
from os.path import join
from exchange_enum import ExchangeEnum
from config import get_config

cfg = get_config()

__all__ = [
    'download_pk',
]


def _save_data(filename, data):
    file_p = join(cfg.get_raw_data_path(), filename)
    tmp_file_p = file_p + '.tmp'
    with open(tmp_file_p, "wb") as fp:
        pickle.dump(data, fp, protocol=pickle.HIGHEST_PROTOCOL)
    os.rename(tmp_file_p, file_p)
    pass


def _download_huobi_pk():
    # 下载huobi基础数据
    from ref.HuobiServices import get_symbols
    symbol_info = get_symbols()
    _save_data('huobi_symbol_info.pk', symbol_info)
    pass


def _download_okex_pk():
    # 下载okex基础数据
    okex_pairs_increment_p = join(cfg.get_raw_data_path(), 'okex_symbol_info.csv')
    if not os.path.exists(okex_pairs_increment_p):
        print('okex 没有提供基础数据下载接口，只有文件okex_symbol_info.csv')
        print("币对精度文件%s 不存在"%(okex_pairs_increment_p))
    pass


def _download_binance_pk():
    # 下载binance基础数据
    from binance.client import Client
    client = Client('api_key', 'api_secret')
    exchange_info = client.get_exchange_info()
    _save_data('binance_exchange_info.pk', exchange_info)
    # 下载 symbol信息
    symbol_info_dic = {}
    for sym in exchange_info['symbols']:
        symbol_info = client.get_symbol_info(sym['symbol'])
        symbol_info_dic[sym['symbol']] = symbol_info
    _save_data('binance_symbol_info.pk', symbol_info_dic)
    pass


def _download_bitfinex_pk():
    # 下载bitfinex基础数据
    url = "https://api.bitfinex.com/v1/symbols_details"
    response = requests.request("GET", url)
    symbol_info = json.loads(response.text)
    _save_data('bitfinex_symbol_info.pk', symbol_info)
    pass


def _download_bibox_pk():
    # 下载bibox基础数据
    url = "https://api.bibox.com/v1/mdata?cmd=pairList"
    response = requests.request("GET", url)
    symbol_info = json.loads(response.text)
    if 'result' not in symbol_info:
        print('获取bibox交易所币对失败')
        return
    _save_data('bibox_symbol_info.pk', symbol_info)
    pass


def _download_zb_pk():
    # 下载zb基础数据
    url = "http://api.zb.cn/data/v1/markets"
    response = requests.request("GET", url)
    symbol_info = json.loads(response.text)
    _save_data('zb_symbol_info.pk', symbol_info)
    pass


def _download_bigone_pk():
    # 下载bigone基础数据
    url = "https://big.one/api/v2/markets"
    response = requests.request("GET", url)
    symbol_info = json.loads(response.text)
    _save_data('bigone_symbol_info.pk', symbol_info)
    pass


def _download_kucoin_pk():
    # 下载kucoin基础数据
    url = 'https://api.kucoin.com/v1/market/open/symbols'
    response = requests.request("GET", url)
    symbol_info = json.loads(response.text)
    _save_data('kucoin_symbol_info.pk', symbol_info)
    pass


def _download_fcoin_pk():
    # 下载fcoin基础数据
    url = 'https://api.fcoin.com/v2/public/symbols'
    response = requests.request("GET", url)
    symbol_info = json.loads(response.text)
    _save_data('fcoin_symbol_info.pk', symbol_info)
    pass


def _download_binmex_pk():
    # 下载binmex基础数据
    url = 'https://www.bitmex.com/api/v1/instrument'
    response = requests.request("GET", url)
    symbol_info = json.loads(response.text)
    _save_data('binmex_symbol_info.pk', symbol_info)
    pass


def _download_otcbtc_pk():
    # 下载otcbtc基础数据
    url = 'https://bb.otcbtc.com/api/v2/markets'
    response = requests.request("GET", url)
    symbol_info = json.loads(response.text)
    _save_data('otcbtc_symbol_info.pk', symbol_info)
    pass


def _download_all_pk():
    _download_huobi_pk()
    _download_okex_pk()
    _download_binance_pk()
    _download_bitfinex_pk()
    _download_bibox_pk()
    _download_zb_pk()
    _download_bigone_pk()
    _download_kucoin_pk()
    _download_fcoin_pk()
    _download_binmex_pk()
    _download_otcbtc_pk()
    pass


def download_pk(exchange):
    # 下载pk数据
    if type(exchange) is str:
            exchange = getattr(ExchangeEnum, exchange)
    if exchange is ExchangeEnum.huobi:
        _download_huobi_pk()
    elif exchange is ExchangeEnum.okex:
        _download_okex_pk()
    elif exchange is ExchangeEnum.binance:
        _download_binance_pk()
    elif exchange is ExchangeEnum.bitfinex:
        _download_bitfinex_pk()
    elif exchange is ExchangeEnum.bibox:
        _download_bibox_pk()
    elif exchange is ExchangeEnum.zb:
        _download_zb_pk()
    elif exchange is ExchangeEnum.bigone:
        _download_bigone_pk()
    elif exchange is ExchangeEnum.kucoin:
        _download_kucoin_pk()
    elif exchange is ExchangeEnum.fcoin:
        _download_fcoin_pk()
    elif exchange is ExchangeEnum.binmex:
        _download_binmex_pk()
    elif exchange is ExchangeEnum.otcbtc:
        _download_otcbtc_pk()
    else:
        _download_all_pk()
    pass


if __name__ == '__main__':
    print('初始化基础数据')
    t1 = time.time()
    download_pk(ExchangeEnum.all_ex)
    t2 = time.time()
    print(t2-t1)
    pass