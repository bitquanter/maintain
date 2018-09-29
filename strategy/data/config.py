# coding:utf-8
import os
import sys
from os.path import join

_cfg = None


class dataConfig(object):

    def __init__(self):
        self.BUNDLE_PATH = 'D:\\bundle'
        pass

    def get_bcolz_data_path(self, code, unit='1d', makedir=False):
        # bcolz 行情存储目录
        assert unit in ('1m', '5m', '15m', '30m', '60m', '120m', '1d', '1w', 'mn') # mn 表示一月
        exchange = code.split("/")[0]
        p = join(self.BUNDLE_PATH, unit, exchange, code)
        if not os.path.exists(p) and makedir:
            os.makedirs(p)
        return p

    def get_bcolz_day_path(self, code, makedir=False):
        # bcolz 天行情存储目录
        exchange = code.split("/")[0]
        p = join(self.BUNDLE_PATH, "1d", exchange, code)
        if not os.path.exists(p) and makedir:
            os.makedirs(p)
        return p


    def get_bcolz_minute_path(self, code, makedir=False):
        # bcolz 分钟行情存储目录
        exchange = code.split("/")[0]
        p = join(self.BUNDLE_PATH, "1m", exchange, code)
        if not os.path.exists(p) and makedir:
            os.makedirs(p)
        return p



def get_config():
    global _cfg
    if not _cfg:
        _cfg = dataConfig()
    return _cfg
