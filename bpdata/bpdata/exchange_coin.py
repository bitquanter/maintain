# coding:utf-8
import json
bp_coin_pair = {}

def get_trade_symbol(exchange):
    '''
    返回指定交易所币对字典
    '''
    if exchange not in bp_coin_pair:
        return None
    else:
        return bp_coin_pair[exchange]
    pass


def get_all_tick_keys():
    '''
    获取所有ticker redis键
    '''
    keys = []
    for exchange in bp_coin_pair:
        for base_currency in bp_coin_pair[exchange]:
            for trade_currency in bp_coin_pair[exchange][base_currency]:
                key = 'tick/%s/%s%s'%(exchange, trade_currency, base_currency)
                keys.append(key)
    return keys
    pass


def get_all_depth_keys():
    '''
    获取所有depth redis键
    '''
    keys = []
    for exchange in bp_coin_pair:
        for base_currency in bp_coin_pair[exchange]:
            for trade_currency in bp_coin_pair[exchange][base_currency]:
                key = 'depth/%s/%s%s'%(exchange, trade_currency, base_currency)
                keys.append(key)
    return keys
    pass


def _get_symbol_from_db():
    '''
    从数据库查询币对信息
    '''
    from bp_db import DbUtil
    db = DbUtil()
    WIDE_USED = True
    res = {}
    symbols = db.get_all_symbol_info(WIDE_USED)
    for sym in symbols:
        if sym.exchange not in res:
            res[sym.exchange] = {}
        if sym.quote_currency not in res[sym.exchange]:
            res[sym.exchange][sym.quote_currency] = []
        res[sym.exchange][sym.quote_currency].append(sym.base_currency)
    return res
    pass

bp_coin_pair = _get_symbol_from_db()
