# -*- coding: utf-8 -*-
import FuBot
from GlobalConfig import *
import IRCFonts
import os
import json
import time
import re
import urllib2
from Kafe import Kafe
class BotFly(FuBot.FuBot):

  def __init__(self, host, port, nick, ident, realname):
    super(BotFly, self).__init__(host, port, nick, ident, realname)

  def cmd(self, command, args, channel, **kwargs):
    super(BotFly, self).cmd(command, args, channel, **kwargs)
    if VERBOSE: print "COMMAND BotFly!"
    print command
    if command == 'metern':
      self.msg(channel, self.metern())
    elif command == 'middag':
      for rett in self.middag():
        self.msg(channel, rett)

  def metern(self):
    response = os.popen('rwho').readlines()
    maskiner = re.compile('sorterytter|spartiate|regent|reigersber|soleil|speedwell|quittance|ramilles|starrenburg|slesvig|repulse|skjold|spes|stcroix|vengance|sejer')
    pattern = re.compile('.::0.')
    response = [line.split(" ")[0] for line in response if pattern.search(line) and maskiner.search(line)]
    return "Disse er på metern nå: " + ", ".join(response)

  def middag(self):
    kafe = Kafe('Informatikkafeen')
    print kafe.todaysDinner()
    return kafe.todaysDinner()

if __name__ == '__main__':
  HOST = 'irc.ifi.uio.no'
  PORT = 6667
  NICK = 'BotFly'
  IDENT = 'BotFly'
  REALNAME = 'Botfly'
  OWNER = 'Jonasac'

  bot = BotFly(HOST, PORT, NICK, IDENT, REALNAME)
  bot.connect()
  bot.join('#nybrummbot')
  bot.start()
