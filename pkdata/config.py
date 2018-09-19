# coding:utf-8
import random
import os
from os.path import join
_cfg = None


class pkConfig(object):

    def __init__(self):
        self.BUNDLE_PATH = os.path.dirname(os.path.realpath(__file__))
        self.RAW_DATA_PATH = join(self.BUNDLE_PATH, 'raw_data')
        self.OUTPUTS_PATH = join(self.BUNDLE_PATH, 'outputs')
        self.DB_FILE = join('sqlite:///%s' % (self.OUTPUTS_PATH,), "symbols.db")
        self.EXCHANGE_PRIORITY = ['huobi', 'okex', 'binance', 'bitfinex', 'bibox', 'zb', 'bigone', 'kucoin', 'fcoin', 'binmex', 'otcbtc']
        pass

    def get_bundle_path(self):
        return self.BUNDLE_PATH

    def get_raw_data_path(self):
        return self.RAW_DATA_PATH

    def get_outputs_path(self):
        return self.OUTPUTS_PATH

    def get_sqlite_db_uri(self):
        return self.DB_FILE

    def get_exchange_priority(self):
        return self.EXCHANGE_PRIORITY
        pass



def get_config():
    global _cfg
    if not _cfg:
        _cfg = pkConfig()
    return _cfg
