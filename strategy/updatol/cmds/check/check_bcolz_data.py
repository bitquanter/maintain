#!/usr/bin/env python.py
#-*- coding: utf-8 -*-

import os
import bcolz
import click


@click.command()
@click.option('-s', '--coin', default='ALL', help='币对代码，ALL表示所有')
@click.option('-p', '--processes', default=0, help='线程数,默认只有一个')
@click.pass_context
@measure_time
def check_bcolz_data(ctx, coin, processes):
    """check bcolz data"""
    print('TODO:check_bcolz_data')
