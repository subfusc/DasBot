#!/usr/bin/env python
# -*- coding: utf-8 -*-

from GlobalConfig import *
from Regex import *
import BeautifulSoup as bs
import IRCbot
import urllib2
import re

FUDEBUG = True

class FuBot(IRCbot.IRCbot):

    def __init__(self, host, port, nick, ident, realname):
        super(FuBot,self).__init__(host, port, nick, ident, realname)

    def listen(self, command, msg, channel, **kwargs):

        url_match = re.search(URLREGEX,msg)

        if (url_match):
            page_content = self.get_page_content(url_match.group()) 
            page_title = self.get_page_title(page_content)
            self.msg(channel,"Tittel -- "+page_title) if page_title else None


    def get_page_content(self, page_url):
        """ Returns the content of a page."""
        page_req = urllib2.Request(page_url, headers={'User-Agent' : "Magic Browser"}) 
        try:
            page_content = urllib2.urlopen(page_req)
        except urllib2.URLError, (err):
            print "%s" % (err)
            return None
        return page_content


    def get_page_title(self, page_content):
        """ 
        Returns the title contained in a page.
        !! Needs to pay more attention to different charsets within the title. !!
        """
        page_soup = bs.BeautifulSoup(page_content)
        page_title = page_soup.title.string
        page_title = page_title.strip().replace("\n","").encode('utf-8')
        return page_title if page_title else None


if __name__ == '__main__':
  HOST = 'irc.ifi.uio.no'
  PORT = 6667
  NICK = 'FuBot'
  IDENT = 'FuBot'
  REALNAME = 'FuBot'
  OWNER = 'wictorht'

  bot = FuBot(HOST, PORT, NICK, IDENT, REALNAME)
  bot.connect()
  bot.join('#fubot')
  bot.start()
