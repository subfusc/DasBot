# -*- coding:utf-8 -*-
from GlobalConfig import *
UNDERLINED = "\x1F"
BOLD = '\x02'
REVERSED = '\x16'
RESET = '\x0F'

def bold(string):
    return BOLD + string + RESET

def underline(string):
    return UNDERLINED + string + RESET

def reverse(string):
    return REVERSED + string + RESET
