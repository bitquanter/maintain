# coding:utf-8
import json
bp_coin_pair = {}
# 火币币对
huobi_coin = {}
huobi_coin['btc'] = ['eos','ada','trx','ltc','eth','iota','xrp','bch','but','ht']
huobi_coin['usdt'] = ['btc','ada','iota','xrp','ltc','eos','eth','trx','bch','ht']
huobi_coin['eth'] = ['iota','ada','trx','eos','but','ht']
bp_coin_pair['huobi'] = huobi_coin
# OK币对
ok_coin = {}
ok_coin['btc'] = ['xlm','okb']
ok_coin['eth'] = ['ltc','xrp','xlm','bch','okb']
ok_coin['usdt'] = ['xlm', 'okb']
bp_coin_pair['okex'] = ok_coin
# 币安币对
bib_coin = {}
bib_coin['btc'] = ['bnb']
bib_coin['eth'] = ['bnb']
bib_coin['usdt'] = ['bnb']
bp_coin_pair['binance'] = bib_coin
# bitfinex 币对
bitfinex_coin = {}
bp_coin_pair['bitfinex'] = bitfinex_coin
# bibox币对
bix_coin = {}
bix_coin['btc'] = ['bix']
bix_coin['eth'] = ['bix']
bix_coin['usdt'] = ['bix']
bp_coin_pair['bibox'] = bix_coin
# zb币对
zb_coin = {}
zb_coin['usdt'] = ['zb']
zb_coin['btc'] = ['zb']
zb_coin['zb'] = ['eth']
bp_coin_pair['zb'] = zb_coin
# kucoin币对
kucoin_coin = {}
kucoin_coin['btc'] = ['kcs']
kucoin_coin['usdt'] = ['kcs']
kucoin_coin['eth'] = ['kcs']
bp_coin_pair['kucoin'] = kucoin_coin
# fcoin币对
fcoin_coin = {}
fcoin_coin['btc'] = ['ft']
fcoin_coin['eth'] = ['ft']
fcoin_coin['usdt'] = ['ft']
bp_coin_pair['fcoin'] = fcoin_coin
# otcbtc币对
otcbtc_coin = {}
otcbtc_coin['btc'] = ['otb']
otcbtc_coin['usdt'] = ['otb']
otcbtc_coin['eth'] = ['otb']
bp_coin_pair['otcbtc'] = otcbtc_coin
# bigone 币对
bigone_coin = {}
bp_coin_pair['bigone'] = bigone_coin
# binmex币对
binmex_coin = {}
bp_coin_pair['binmex'] = binmex_coin



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
