# -*- coding:utf-8 -*-
import GlobalConfig as conf

UNDERLINED = "\x1F"
BOLD = '\x02'
REVERSED = '\x16'
COLOR = '\x03'
RESET = '\x0F'

COLORS = { 'white':'00', 'black':'01', 'navy':'02', 'green':'03',
           'red':'04', 'brown':'05', 'purple':'06', 'olive':'07',
           'yellow':'08', 'lime':'09', 'teal':'10', 'cyan':'11',
           'blue':'12', 'pink':'13', 'gray':'14', 'silver':'15'}

def bold(string):
    return BOLD + string + RESET

def underline(string):
    return UNDERLINED + string + RESET

def reverse(string):
    return REVERSED + string + RESET

def green(string):
    return COLOR + COLORS['green'] + string + COLOR

def red(string):
    return COLOR + COLORS['red'] + string + COLOR

def blue(string):
    return COLOR + COLORS['blue'] + string + COLOR
