# coding: utf-8
import logging
import sys
import datetime
import numpy as np
import os
from os.path import join
import json


def setup_basic_logging(debug=False):
    format = '[%(asctime)s] %(name)-8s %(levelname)-5s %(message)s'

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(logging.Formatter(format))

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(logging.Formatter(format))
    stderr_handler.setLevel('ERROR')

    logging.getLogger().addHandler(stdout_handler)
    logging.getLogger().addHandler(stderr_handler)
    logging.getLogger().setLevel('DEBUG' if debug else 'INFO')


def parse_date(s):
    return datetime.date(*map(int, s.split('-')))


def parse_time(time):
    return datetime.time(*map(int, time.split(':')))


def dt2ts(dt):
    if isinstance(dt, datetime.datetime):
        epoch = datetime.datetime(1970, 1, 1)
    else:
        epoch = datetime.date(1970, 1, 1)
    td = dt - epoch
    return td.seconds + td.days * 86400


def ts2dt(ts):
    return datetime.datetime.utcfromtimestamp(int(ts))


def float2ts(f):
    dt = datetime.datetime.strptime(str(int(f)), "%Y%m%d")
    return dt2ts(dt)


def date2dt(date):
    return datetime.datetime.combine(date, datetime.time.min)


v_dt2ts = np.vectorize(dt2ts, otypes=[np.int])
v_float2ts = np.vectorize(float2ts, otypes=[np.int])


def float_or_nan(x):
    try:
        return float(x)
    except Exception as e:
        return float('nan')


def record_tick_active(check):
    '''
    数据存档
    '''
    base_dir = '/data/logs/'
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    path = join(base_dir, check['time'].split('_')[0])
    if not os.path.exists(path):
        os.makedirs(path)
    file_name = '%s_tick_active_%s_lost_%s.json'%(check['time'],check['active_count'],check['lost_count'])
    file_p = join(path, file_name)
    with open(file_p, "w") as f:
        json.dump(check, f)
    pass
