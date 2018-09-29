#!/usr/bin/env python.py
#-*- coding: utf-8 -*-
    
import datetime
import os
import click
import bcolz
import pandas as pd

@click.command()
@click.option('-s', '--security', default='huobi/btc.usdt', help=u'币对代码')
@click.option('-b', '--begin', default='', help=u'开始日期,例如2017-10-01')
@click.option('-e', '--end', default='', help=u'结束日期,例如2017-11-01')
@click.option('-h', '--head', default=0, help=u'前面多少条数据')
@click.option('-t', '--tail', default=0, help=u'末尾多少条数据')
@click.pass_context
def look_bcolz_minute(ctx, security, begin, end, head, tail):
    '''
    查看bcolz分钟数据
    '''
    print('TODO:look_bcolz_minute')
