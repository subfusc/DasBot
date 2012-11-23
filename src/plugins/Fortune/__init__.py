# -*- coding: utf-8 -*- 
from GlobalConfig import *
from random import randint

MAXLINEWIDTH = 79

class Plugin(object):

    def cmd(self, command, args, channel, **kwargs):
        if command == "fortune":
            return [(0, channel, self.fortune())]
    
    def help(self, command, args, channel, **kwargs):
        if command == "fortune":
            return [(1, kwargs["from_nick"], 
            "!{} prints a random, hopefully interesting, adage.".format("fortune"))]
        if command == "all":
            return [(1, kwargs["from_nick"], 
            "Fortune: {ftn}".format(ftn = "fortune"))]

    def fortune(self):
        fortunes = "data/fortunes.txt"
        raw_fort = open(fortunes).read().split("%")
        small_fort = list()
        for f in raw_fort:
            if len(f) <= MAXLINEWIDTH:
                small_f = f.strip().replace("\t","").replace("\n"," ")
                small_fort.append(small_f)
        index = randint(0,len(small_fort)-1)
        return small_fort[index]
