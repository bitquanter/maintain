#!/usr/bin/env python.py
#-*- coding: utf-8 -*-
    
from .check import check_commands
from .check import *
from .create import create_commands
from .create import *
from .look import look_commands
from .look import *
from .update import update_commands
from .update import *

all_commands = check_commands + \
    create_commands + \
    look_commands + \
    update_commands

__all__ = [
    str(cmd.name) for cmd in all_commands
]
