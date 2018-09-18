# coding:utf-8
import os
import sys
from os.path import join
from exchange_coin import get_trade_symbol

_cfg = None


class BpdataConfig(object):

    def __init__(self):
        self.BUNDLE_PATH = os.path.dirname(os.path.realpath(__file__))
        self.redis_url = 'localhost:6379'
        self.ID = 'id1'
        self.DB_FILE = join('sqlite:///%s' % (self.BUNDLE_PATH,), "_bpdata.db")
        pass

    def get_symbols(self,exchange):
        return get_trade_symbol(exchange)
        pass

    def get_id(self):
        return self.ID
        pass

    def get_redis_url(self):
        return self.redis_url
        pass

    def get_sqlite_db_uri(self):
        return self.DB_FILE



def get_config():
    global _cfg
    if not _cfg:
        _cfg = BpdataConfig()
    return _cfg
