#!/usr/bin/env python.py
# -*- coding: utf-8 -*-

import os
import bcolz
import click
import datetime


@click.command()
@click.option('-s', '--coin', default='huobi/btc.usdt')
@click.option('--overwrite/--no-overwrite', default=False)
@click.option('-p', '--processes', default=0)
@click.pass_context
@measure_time
def create_bcolz_minute_data(ctx, coin, overwrite, processes):
    '''
    创建bcolz格式的行情数据.
    '''
    print('TODO:create_bcolz_minute_data')
