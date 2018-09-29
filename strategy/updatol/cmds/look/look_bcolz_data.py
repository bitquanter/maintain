#!/usr/bin/env python.py
#-*- coding: utf-8 -*-
    
import datetime
import os
import click
import bcolz
import pandas as pd

@click.command()
@click.option('-s', '--security', default='huobi/btc.usdt')
@click.option('-b', '--begin', default='')
@click.option('-e', '--end', default='')
@click.option('-h', '--head', default=0)
@click.option('-t', '--tail', default=0)
@click.option('-u', '--unit', default='5m')
@click.pass_context
def look_bcolz_data(ctx, security, begin, end, head, tail, unit):
    '''
    查看bcolz data
    '''
    print('TODO:look_bcolz_data')
