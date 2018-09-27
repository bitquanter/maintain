#!/usr/bin/env python
# coding: utf-8
import time
import json
from os.path import join
from exchange_enum import ExchangeEnum
from download_raw_data import download_pk
from parse_raw_data import parse_symbol_info
from orm import DbUtil
from config import get_config
from exchange_coin import bp_coin_pair

cfg = get_config()
db = DbUtil()


def update_widely_used_coins():
    '''
    更新常用币对
    '''
    widely_used = []
    for exchange in bp_coin_pair:
        for quote_currency in bp_coin_pair[exchange]:
            for base_currency in bp_coin_pair[exchange][quote_currency]:
                widely_used.append((exchange,base_currency,quote_currency))
    db.reset_widely_used()
    for wu in widely_used:
        db.update_widely_used(wu)
    db.db_commit()
    pass


def init_data():
    '''
    请求基础数据/解析/入库
    '''
    download_pk(ExchangeEnum.all_ex) # 下载数据
    print('完成下载')
    symbols_info = parse_symbol_info(ExchangeEnum.all_ex) # 解析数据
    print(len(symbols_info))
    print('完成解析')
    # 写入数据库
    for symbol in symbols_info:
        db.save_symbol_info(symbol)
    db.db_commit()
    # 更新常用币对状态
    update_widely_used_coins()
    print('完成入库')
    pass


def get_coin_exchange_pair():
    '''
    返回所有币对：交易所字典
    '''
    res = {}
    coin_exchange_pair = db.qry_all_coin_exchange_pair()
    if not coin_exchange_pair:
        return res
    for symbol, exchange in coin_exchange_pair:
        if symbol not in res:
            res[symbol] = []
        res[symbol].append(exchange)
    # 根据交易所优先级筛选
    ex_p = cfg.get_exchange_priority()
    for sym, exs in res.items():
        if len(exs) == 1:
            res[sym] = exs[0]
        else:
            for ex in ex_p:
                if ex in exs:
                    res[sym] = ex
                    break
    p = join(cfg.get_outputs_path(), 'coin_exchange_map.json')
    with open(p, "w") as f:
        json.dump(res,f)
    return res


def get_exchange_coin_pair():
    '''
    返回所有交易所:币对字典
    '''
    res = {}
    coin_exchange_pair = db.qry_all_coin_exchange_pair()
    if not coin_exchange_pair:
        return res
    for symbol, exchange in coin_exchange_pair:
        if exchange not in res:
            res[exchange] = []
        res[exchange].append(symbol)
    p = join(cfg.get_outputs_path(), 'exchange_coin_map.json')
    with open(p, "w") as f:
        json.dump(res,f)
    return res


def get_exchange_contraint():
    '''
    生成coin常量集合
    '''
    coin_constraints = {}
    all_symbol_info = db.qry_all()
    if not all_symbol_info:
        print('no data in database')
        return {}
    coin_exchange_pair = get_coin_exchange_pair()
    for asl in all_symbol_info:
        if asl.exchange == coin_exchange_pair[asl.symbol]:
            if asl.exchange not in coin_constraints:
                coin_constraints[asl.exchange] = {}
            if asl.symbol not in coin_constraints[asl.exchange]:
                coin_constraints[asl.exchange][asl.symbol] = {}    
            coin_constraints[asl.exchange][asl.symbol]['price_precision'] = asl.price_precision
            coin_constraints[asl.exchange][asl.symbol]['amount_precision'] = asl.amount_precision
            coin_constraints[asl.exchange][asl.symbol]['min_amount'] = asl.min_amount
    p = join(cfg.get_outputs_path(), 'coin_constraints.json')
    with open(p, "w") as f:
        json.dump(coin_constraints,f)
    return coin_constraints
    pass


def get_exchange_quote_base():
    res = {}
    all_symbol_info = db.qry_all()
    if not all_symbol_info:
        print('no data in database')
    for asl in all_symbol_info:
        if asl.exchange not in res:
            res[asl.exchange] = {}
        if asl.quote_currency not in res[asl.exchange]:
            res[asl.exchange][asl.quote_currency] = []
        res[asl.exchange][asl.quote_currency].append(asl.base_currency)
    for k in res:
        print('===================================')
        print('exchange:',k)
        for s in res[k]:
            print(s,res[k][s])
    pass


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-t', '--task', default='init')
    options = parser.parse_args()
    if options.task == 'init':
        init_data()
    elif options.task == 'coin_exchange':
        get_coin_exchange_pair()
    elif options.task == 'exchange_coin':
        get_exchange_coin_pair()
    elif options.task == 'contraint':
        get_exchange_contraint()
    else:
        print('invalid task')
    pass
