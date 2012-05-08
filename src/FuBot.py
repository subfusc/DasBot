# -*- coding: utf-8 -*-

from GlobalConfig import *
from Regex import *
import BeautifulSoup as bs
import IRCbot
import urllib2
import os
import re

class FuBot(IRCbot.IRCbot):

    def __init__(self, host, port, nick, ident, realname):
        super(FuBot,self).__init__(host, port, nick, ident, realname)

    def cmd(self, command, args, channel, **kwargs):
        if command == "gr":
            a = args.split()
            if len(a) == 1:
                w = GramWord(a[0])
                if w.is_grammatical():
                    self.msg(channel,"Word \""+w.get_word()+"\" is grammatical.")
                else:
                    self.msg(channel,"Word \""+w.get_word()+"\" is not grammatical.")
            else:
                self.msg(channel,"usage: !gr [ word | term | utterance ]")


    def listen(self, command, msg, channel, **kwargs):
        url_match = re.search(URLREGEX,msg)
        if (url_match):
            t = UrlTitle(url_match.group()).get()
            self.msg(channel,"Title: "+t) if t else None
        

class GramWord:
    
    dictd = None
    dicts = None
    word = None

    def __init__(self, w):
        self.dictd = "/usr/share/dict"
        self.dicts = os.listdir(self.dictd)
        self.word = w

    def is_grammatical(self):
        if len(self.dicts):
            gr = False
            for df in self.dicts:
                f = open(self.dictd+"/"+df).read().split()
                if self.word.lower() in f:
                    gr = True
            return gr

    def get_word(self):
        return self.word


class UrlTitle:
    
    page_url = None
    page_title = None
    page_content = None

    def __init__(self,page_url):
        self.page_url = page_url
        self.get_page_content() 
        self.get_page_title()

    def get_page_content(self):
        """ Gets the content of a page."""
        page_req = urllib2.Request(self.page_url, 
                headers={'User-Agent' : "Magic Browser"}) 
        try:
            self.page_content = urllib2.urlopen(page_req)
        except urllib2.URLError, (err):
            print "%s" % (err)
            page_content = None

    def get_page_title(self):
        """ 
        Gets the title contained in a page.
        !! Needs to pay more attention to different charsets within the title. !!
        """
        page_soup = bs.BeautifulSoup(self.page_content)
        title = page_soup.title.string
        title = title.strip().replace("\n","").encode('utf-8')
        self.page_title = title if title else None

    def get(self):
        return self.page_title
    

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
