# -*- coding: utf-8 -*-
import sys
import six
import numpy as np
import pandas as pd
import datetime
from .data_utils import (#convert_security,
    convert_dt,
    frequency_compat,
    ensure_str_tuple,
    check_unit_fields,
    DEFAULT_FIELDS,
    is_list,
    group_array,)
from .datalib import get_price_daily_single
from .datalib import get_price_minute_single
from .datetime_utils import vec2datetime, vec2combine, vec2date, vec2timestamp, to_timestamp, to_datetime
from .exceptions import ParamsError


def get_trade_days(end_date, count):
	pass


def get_price(security, start_date=None, end_date=None, frequency='minute', fields=None, count=None):
    '''
    获取标的行情数据
    
    Args:
        security: 标的 
        start_date: 开始日期
        end_date: 结束日期
        frequency: 周期
        fields: 字段
        count: 取数据条数

    Returns:
        pandas.DataFrame
    '''
    #security = convert_security(security)

    if count is not None and start_date is not None:
        raise ParamsError("get_price 不能同时指定 start_date 和 count 两个参数")

    if count is not None:
        count = int(count)

    end_dt = convert_dt(end_date) if end_date else datetime.datetime(2015, 12, 31)

    start_dt = convert_dt(start_date) if start_date else datetime.datetime(2015, 1, 1)

    if frequency in frequency_compat:
        unit = frequency_compat.get(frequency)
    else:
        unit = frequency

    if fields is not None:
        fields = ensure_str_tuple(fields)
    else:
        fields = tuple(DEFAULT_FIELDS)


    check_unit_fields(unit, fields)
    group = int(unit[:-1])
    res = {}
    for s in (security if is_list(security) else [security]):
        if unit.endswith('d'):
            a, index = get_price_daily_single(
                s,
                end_date=end_dt.date(),
                start_date=start_dt.date() if start_dt else None,
                count=count * group if count is not None else None,
                fields=fields,
                include_now=True)
        else:
            a, index = get_price_minute_single(
                s,
                end_dt=end_dt,
                start_dt=start_dt,
                count=count * group if count is not None else None,
                fields=fields,
                include_now=True)

        # group it
        dict_by_column = {f: group_array(a[f if f != 'price' else 'avg'], group, f) for f in fields}
        if index is not None and len(index) > 0:
            index = group_array(index, group, 'index')
            index = vec2datetime(index)
        res[s] = dict(index=index, columns=fields, data=dict_by_column)


    if is_list(security):
        fields = fields or DEFAULT_FIELDS
        if len(security) == 0:
            return pd.Panel(items=fields)
        pn_dict = {}
        index = res[security[0]]['index']
        for f in fields:
            df_dict = {s:res[s]['data'][f] for s in security}
            pn_dict[f] = pd.DataFrame(index=index, columns=[s for s in security], data=df_dict)
        return pd.Panel(pn_dict)
    else:
        return pd.DataFrame(**res[security])
