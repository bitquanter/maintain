#!/usr/bin/env python.py
# -*- coding: utf-8 -*-

import os
import bcolz
import click
import datetime
from ..create.create_bcolz_day_data import _create_bcolz_day_data


@click.command()
@click.option('-s', '--security', default='huobi/btc.usdt')
@click.option('--create/--no-create', default=True)
@click.option('-p', '--processes', default=0)
@click.pass_context
@measure_time
def update_bcolz_day_data(ctx, security, create, processes):
    '''
    更新bcolz天行情数据
    '''
    print('TODO:update_bcolz_day_data')
