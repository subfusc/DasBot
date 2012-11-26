# -*- coding: utf-8 -*-

from GlobalConfig import *
import os

class Plugin(object):

    def __init__(self):
        self.sources = { "/usr/share/dict" : "EN", "data" : "NO" }
        self.files = []

    def cmd(self, command, args, channel, **kwargs):
        if command == "gr":
            if args:
                return [(0, channel, self.gram(args.split()[0]))]
            else:
               return self.help(command, args, channel,**kwargs)

    def help(self, command, args, channel, **kwargs):
        if command == "gr":
            return [(1, kwargs["from_nick"],
            "!{} [word] determines if the spelling of the given word is correct.".format("gr"))]
        if command == "all":
            return [(1, kwargs["from_nick"],
            "Dict: {gr}".format(gr = "gr"))]

    def gram(self, token):
        for s in self.sources.keys():
            try:
                for f in os.listdir(s):
                    if f.endswith(".words"):
                        self.files.append(os.path.join(s,f))
            except OSError as e:
                print "Misc: {}".format(e)

        lang = set()
        for f in self.files:
            if token in open(f).read().split():
                lang.add(self.sources[os.path.dirname(f)])
                
        if lang:
            return "{t}{l} is grammatical".format(l = list(lang), t = token)
        return "{t} is not grammatical".format(t = token)
