#!/usr/bin/env python.py
# -*- coding: utf-8 -*-
import datetime
import os
import click
import bcolz
import numpy as np
from ..create.create_bcolz_minute_data import _create_bcolz_minute_data



@click.command()
@click.option('-s', '--security', default='huobi/btc.usdt')
@click.option('--create/--no-create', default=True)
@click.option('-p', '--processes', default=0)
@click.pass_context
@measure_time
def update_bcolz_minute_data(ctx, security, create, processes):
    '''
    更新bcolz分钟数据
    '''
    print('TODO:update_bcolz_minute_data')
