#!/usr/bin/env python.py
#-*- coding: utf-8 -*-

from __future__ import print_function

import sys
import os
import logging
import pandas as pd
import click
from os.path import abspath, dirname, join



@click.group()
@click.pass_context
def cli(ctx):
    import socket
    ctx.obj['HOSTNAME'] = socket.gethostname()

    import bcolz
    bcolz.set_nthreads(1)
    # logging.basicConfig(stream=sys.stdout, level='DEBUG' if debug else 'INFO')
    # logger.error('Debug mode is %s' % ('on' if debug else 'off'))
    pd.set_option('display.max_rows', 100000000)
    pd.set_option('display.max_columns', 100000000)
    pd.set_option('display.width', 100000000)


from .cmds import all_commands
for cmd in all_commands:
    cli.add_command(cmd)


def entry_point():
    cli(obj={})

if __name__ == "__main__":
    entry_point()

