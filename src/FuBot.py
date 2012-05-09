# -*- coding: utf-8 -*-

from GlobalConfig import *
from Regex import *
import BeautifulSoup as bs
import DebugBot
import urllib2
import random
import sys
import os
import re

TALK_REGEX = r"^FuBot:.*$"
gram_cmd = "gr"
fortune_cmd = "fortune"

class FuBot(DebugBot.DebugBot):
    

    def __init__(self, host, port, nick, ident, realname):
        super(FuBot,self).__init__(host, port, nick, ident, realname)


    def help(self, command, args, channel, **kwargs):
        super(FuBot, self).help(command, args, channel, **kwargs)
        if command == gram_cmd:
            help_msg = "!"+gram_cmd+" [word] determines if the spelling of the given word is correct."
            self.notify(kwargs["from_nick"], help_msg)
        elif command == fortune_cmd:
            help_msg = "!"+fortune_cmd+" prints a random, hopefully interesting, adage."
            self.notify(kwargs["from_nick"], help_msg)


    def cmd(self, command, args, channel, **kwargs):
        super(FuBot, self).cmd(command, args, channel, **kwargs)
        if command == gram_cmd:
            if args:
                self.msg(channel, self.gram(args))
            else:
                self.help(command, args, channel,**kwargs)
        elif command == fortune_cmd:
            self.msg(channel, self.fortune())


    def listen(self, command, msg, channel, **kwargs):
        url_match = re.search(URLREGEX,msg)
        talk_match = re.match(TALK_REGEX,msg,re.IGNORECASE)

        if url_match:
            t = self.urltitle(url_match.group())
            self.msg(channel,"Title: "+t) if t else None
        elif talk_match:
            self.msg(channel,"Yes, my liege?")
        

    def gram(self, args):
        argv = args.split()
        w = GramWord(argv[0])
        if w.is_grammatical():
            return "{}{} is grammatical.".format(argv[0],w.get_lang())
        else:
            return "{} is not grammatical.".format(argv[0])


    def fortune(self):
        fortunes = "data/fortunes.txt"
        raw_fort = open(fortunes).read().split("%")
        small_fort = list()
        for f in raw_fort:
            if len(f) <= 79:
                small_f = f.strip().replace("\t","").replace("\n"," ")
                small_fort.append(small_f)
        index = random.randint(0,len(small_fort)-1)
        return small_fort[index]
        

    def urltitle(self, url):
        req = urllib2.Request(url, headers={'User-Agent':"Magic Browser"}) 
        try:
            page_content = urllib2.urlopen(req)
        except urllib2.URLError, (err):
            print "%s" % (err)
            return
        page_soup = bs.BeautifulSoup(page_content)
        title = page_soup.title.string
        title = title.strip().replace("\n","").encode('utf-8')
        return title if title else None


class GramWord:
    
    dict_dir = "/usr/share/dict/"
    dict_nor = "data/norskeord.txt"
    dict_files = []
    word = None
    lang = []

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
                    self.lang = ["NO"]
                    no_gr = True
                else:
                    self.lang = ["EN"]
                    en_gr = True
                found = True
        if (en_gr and no_gr):
            self.lang = ["NO"]+["EN"]
        return found

    def get_lang(self):
        return self.lang


if __name__ == '__main__':
    HOST = 'irc.ifi.uio.no'
    PORT = 6667
    NICK = 'FuBot'
    IDENT = 'FuBot'
    REALNAME = 'FuBot'
    OWNER = 'wictorht'
    
    bot = FuBot(HOST, PORT, NICK, IDENT, REALNAME)
    bot.connect()
    bot.join("#fubot")
    bot.start()
