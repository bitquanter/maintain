#!/usr/bin/env python
# coding: utf-8
import json
import pickle
import os
import requests
from os.path import join
from exchange_enum import ExchangeEnum
from config import get_config

cfg = get_config()

__all__ = [
    'parse_symbol_info',
]

def _get_float_precision(num):
    num_str = str(num)
    if 'e' in num_str:
        return int(num_str.split('-')[1])
    else:
        return len(num_str.split('.')[1]) if len(num_str.split('.')) > 1 else 0
    pass


def _parse_huobi_symbols_info():
    f = join(cfg.get_raw_data_path(), 'huobi_symbol_info.pk')
    with open(f, "rb") as fp:
        symbols = pickle.load(fp)
        symbols = symbols['data']
    res = []
    for s in symbols:
        item = {}
        item['base_currency'] = s['base-currency']
        item['quote_currency'] = s['quote-currency']
        item['symbol'] = s['base-currency'] + s['quote-currency']
        item['exchange'] = 'huobi'
        item['price_precision'] = s['price-precision']
        item['amount_precision'] = s['amount-precision']
        item['min_amount'] = None
        res.append(item)
    print('huobi len:',len(res))
    return res
    pass


def _parse_okex_symbols_info():
    import pandas as pd
    f = join(cfg.get_raw_data_path(), 'okex_symbol_info.csv')
    okex_precise = pd.read_csv(f)
    res = []
    for index, ok in okex_precise.iterrows():
        item = {}
        item['base_currency'] = ok['currency_pair'].split('_')[0]
        item['quote_currency'] = ok['currency_pair'].split('_')[1]
        item['symbol'] = ok['currency_pair'].replace('_', '')
        item['exchange'] = 'okex'
        item['price_precision'] = ok['price_precision']
        item['amount_precision'] = ok['amount_precision']
        item['min_amount'] = ok['min_amount']
        res.append(item)
    print('okex len:',len(res))
    return res
    pass


def _parse_binance_symbols_info():
    f = join(cfg.get_raw_data_path(), 'binance_symbol_info.pk')
    with open(f, "rb") as fp:
        symbols = pickle.load(fp)
    res = []
    for s in symbols:
        s = symbols[s]
        item = {}
        item['base_currency'] = s['baseAsset'].lower()
        item['quote_currency'] = s['quoteAsset'].lower()
        item['symbol'] = s['baseAsset'].lower() + s['quoteAsset'].lower()
        item['exchange'] = 'binance'
        item['price_precision'] = s['baseAssetPrecision']
        item['amount_precision'] = 8
        item['min_amount'] = s['filters'][1]['minQty']
        res.append(item)
    print('binance len:',len(res))
    return res
    pass


def _parse_bitfinex_symbols_info():
    f = join(cfg.get_raw_data_path(), 'bitfinex_symbol_info.pk')
    with open(f, "rb") as fp:
        symbols = pickle.load(fp)
    res = []
    for s in symbols:
        item = {}
        item['base_currency'] = s['pair'][:-3]
        item['quote_currency'] = s['pair'][-3:]
        item['symbol'] = s['pair']
        item['exchange'] = 'bitfinex'
        item['price_precision'] = s['price_precision']
        item['amount_precision'] = None
        item['min_amount'] = s['minimum_order_size']
        res.append(item)
    print('bitfinex len:',len(res))
    return res
    pass


def _parse_bibox_symbols_info():
    f = join(cfg.get_raw_data_path(), 'bibox_symbol_info.pk')
    with open(f, "rb") as fp:
        symbols = pickle.load(fp)
        symbols = symbols['result']
    res = []
    for s in symbols:
        item = {}
        item['base_currency'] = s['pair'].split('_')[0].lower()
        item['quote_currency'] = s['pair'].split('_')[1].lower()
        item['symbol'] = item['base_currency'] + item['quote_currency']
        item['exchange'] = 'bibox'
        item['price_precision'] = None
        item['amount_precision'] = None
        item['min_amount'] = None
        res.append(item)
    print('bibox len:',len(res))
    return res
    pass


def _parse_zb_symbols_info():
    f = join(cfg.get_raw_data_path(), 'zb_symbol_info.pk')
    with open(f, "rb") as fp:
        symbols = pickle.load(fp)
    res = []
    for k, v in symbols.items():
        item = {}
        item['base_currency'] = k.split('_')[0]
        item['quote_currency'] = k.split('_')[1]
        item['symbol'] = item['base_currency'] + item['quote_currency']
        item['exchange'] = 'zb'
        item['price_precision'] = v['priceScale']
        item['amount_precision'] = v['amountScale']
        item['min_amount'] = None
        res.append(item)
    print('zb len:',len(res))
    return res
    pass


def _parse_bigone_symbols_info():
    f = join(cfg.get_raw_data_path(), 'bigone_symbol_info.pk')
    with open(f, "rb") as fp:
        symbols = pickle.load(fp)
        symbols = symbols['data']
    res = []
    for s in symbols:
        item = {}
        item['base_currency'] = s['baseAsset']['symbol'].lower()
        item['quote_currency'] = s['quoteAsset']['symbol'].lower()
        item['symbol'] = item['base_currency'] + item['quote_currency']
        item['exchange'] = 'bigone'
        item['price_precision'] = s['baseScale']
        item['amount_precision'] = None
        item['min_amount'] = None
        res.append(item)
    print('bigone len:',len(res))
    return res
    pass


def _parse_kucoin_symbols_info():
    f = join(cfg.get_raw_data_path(), 'kucoin_symbol_info.pk')
    with open(f, "rb") as fp:
        symbols = pickle.load(fp)
        symbols = symbols['data']
    res = []
    for s in symbols:
        item = {}
        item['base_currency'] = s['symbol'].split('-')[0].lower()
        item['quote_currency'] = s['symbol'].split('-')[1].lower()
        item['symbol'] = item['base_currency'] + item['quote_currency']
        item['exchange'] = 'kucoin'
        item['price_precision'] = None
        item['amount_precision'] = None
        item['min_amount'] = None
        res.append(item)
    print('kucoin len:',len(res))
    return res
    pass


def _parse_fcoin_symbols_info():
    f = join(cfg.get_raw_data_path(), 'fcoin_symbol_info.pk')
    with open(f, "rb") as fp:
        symbols = pickle.load(fp)
        symbols = symbols['data']
    res = []
    for s in symbols:
        item = {}
        item['base_currency'] = s['base_currency']
        item['quote_currency'] = s['quote_currency']
        item['symbol'] = s['name']
        item['exchange'] = 'fcoin'
        item['price_precision'] = s['price_decimal']
        item['amount_precision'] = s['amount_decimal']
        item['min_amount'] = None
        res.append(item)
    print('fcoin len:',len(res))
    return res
    pass


def _parse_binmex_symbols_info():
    f = join(cfg.get_raw_data_path(), 'binmex_symbol_info.pk')
    with open(f, "rb") as fp:
        symbols = pickle.load(fp)
    res = []
    for s in symbols:
        item = {}
        item['base_currency'] = s['underlying'].lower()
        item['quote_currency'] = s['quoteCurrency'].lower()
        item['symbol'] = item['base_currency'] + item['quote_currency']
        item['exchange'] = 'binmex'
        item['price_precision'] = None
        item['amount_precision'] = None
        item['min_amount'] = None
        res.append(item)
    print('binmex len:',len(res))
    return res
    pass


def _parse_otcbtc_symbols_info():
    f = join(cfg.get_raw_data_path(), 'otcbtc_symbol_info.pk')
    with open(f, "rb") as fp:
        symbols = pickle.load(fp)
    res = []
    for s in symbols:
        item = {}
        item['base_currency'] = s['name'].split('/')[0].lower()
        item['quote_currency'] = s['name'].split('/')[1].lower()
        item['symbol'] = item['base_currency'] + item['quote_currency']
        item['exchange'] = 'otcbtc'
        item['price_precision'] = _get_float_precision(s['trading_rule']['min_price'])
        item['amount_precision'] = _get_float_precision(s['trading_rule']['min_order_volume'])
        item['min_amount'] = s['trading_rule']['min_amount']
        res.append(item)
    print('otcbtc len:',len(res))
    return res
    pass


def _parse_all_symbols_info():
    res = []
    res = _parse_huobi_symbols_info()
    res += _parse_okex_symbols_info()
    res += _parse_binance_symbols_info()
    res += _parse_bitfinex_symbols_info()
    res += _parse_bibox_symbols_info()
    res += _parse_zb_symbols_info()
    res += _parse_bigone_symbols_info()
    res += _parse_kucoin_symbols_info()
    res += _parse_fcoin_symbols_info()
    res += _parse_binmex_symbols_info()
    res += _parse_otcbtc_symbols_info()
    return res
    pass


def parse_symbol_info(exchange):
    # 下载pk数据
    if type(exchange) is str:
            exchange = getattr(ExchangeEnum, exchange)
    if exchange is ExchangeEnum.huobi:
        return _parse_huobi_symbols_info()
    elif exchange is ExchangeEnum.okex:
        return _parse_okex_symbols_info()
    elif exchange is ExchangeEnum.binance:
        return _parse_binance_symbols_info()
    elif exchange is ExchangeEnum.bitfinex:
        return _parse_bitfinex_symbols_info()
    elif exchange is ExchangeEnum.bibox:
        return _parse_bibox_symbols_info()
    elif exchange is ExchangeEnum.zb:
        return _parse_zb_symbols_info()
    elif exchange is ExchangeEnum.bigone:
        return _parse_bigone_symbols_info()
    elif exchange is ExchangeEnum.kucoin:
        return _parse_kucoin_symbols_info()
    elif exchange is ExchangeEnum.fcoin:
        return _parse_fcoin_symbols_info()
    elif exchange is ExchangeEnum.binmex:
        return _parse_binmex_symbols_info()
    elif exchange is ExchangeEnum.otcbtc:
        return _parse_otcbtc_symbols_info()
    else:
        return _parse_all_symbols_info()
    pass


if __name__ == '__main__':
    print('解析原始基础数据')
    res = parse_symbol_info(ExchangeEnum.all_ex)
    print(len(res))
    pass
