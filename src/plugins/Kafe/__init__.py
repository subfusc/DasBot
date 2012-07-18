# -*- coding: utf-8 -*-
import IRCFonts
from Kafe import Kafe
from GlobalConfig import *

class Plugin(object):

  def cmd(self, command, args, channel, **kwargs):
    if DEBUG: print "COMMAND Kafe!"
    if command == 'middag':
        for rett in self.middag():
            return [(0, channel, kwargs['from_nick'], rett)]

  def middag(self):
    kafe = Kafe('Informatikkafeen')
    return kafe.todaysDinner()

