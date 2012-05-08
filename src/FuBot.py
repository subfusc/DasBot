# -*- coding: utf-8 -*-

from GlobalConfig import *
from Regex import *
import BeautifulSoup as bs
import DebugBot
import urllib2
import os
import re

grammar_cmd = "gr"

class FuBot(DebugBot.DebugBot):

    def __init__(self, host, port, nick, ident, realname):
        super(FuBot,self).__init__(host, port, nick, ident, realname)

    def help(self, command, args, channel, **kwargs):
        super(FuBot, self).help(command, args, channel, **kwargs)
        if command == grammar_cmd:
            _msg = "!gr [word] determines if the spelling of the given word is correct"
            self.notify(kwargs["from_user"], _msg)

    def cmd(self, command, args, channel, **kwargs):
        if command == grammar_cmd:
            a = args.split()
            if len(a) == 1:
                w = GramWord(a[0])
                if w.is_grammatical():
                    _str = "['{0}' : {1}] is correct.".format(a[0],w.get_lang())
                    self.msg(channel,_str)
                else:
                    _str = "['{0}'] is not correct.".format(a[0])
                    self.msg(channel,_str)
            else:
                self.help(command, args, channel, **kwargs)

    def listen(self, command, msg, channel, **kwargs):
        url_match = re.search(URLREGEX,msg)
        if (url_match):
            t = UrlTitle(url_match.group()).get()
            self.msg(channel,"Title: "+t) if t else None
        

class GramWord:
    
    dict_dir = "/usr/share/dict/"
    dict_nor = "data/norskeord.txt"
    dict_files = []
    word = None
    lang = None

    def __init__(self, w):
        self.dict_files = [ self.dict_dir+f for f in os.listdir(self.dict_dir)]
        self.dict_files += [ self.dict_nor ]
        self.word = w

    def is_grammatical(self):
        en_gr = False 
        no_gr = False
        found = False
        for df in self.dict_files:
            f = open(df).read().split()
            if self.word.lower() in f:
                if df == self.dict_nor: 
                    self.lang = "NO"
                    no_gr = True
                else:
                    self.lang = "EN"
                    en_gr = True
                found = True
        if (en_gr and no_gr):
            self.lang = "NO, EN"
        return found

    def get_lang(self):
        return self.lang

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
        """Gets the title contained in a page."""
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
  bot.join('#iskbot')
  #bot.join('#fubot')
  bot.start()
