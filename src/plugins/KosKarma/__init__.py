import re
import string
from os import sep
from os import path
from os import makedirs
from KosBackend import KosBackend

class Plugin(object): 

    def __init__(self):
        self.backends = dict()
        self.prefix = "data" + sep + "karma"
        self.suffix = ".karma"
        self.reg = re.compile(r"(\w+\+\+|\w+--|\+\+\w+|--\w+)")

        if not path.isdir(self.prefix):
            makedirs(self.prefix)

    def backend(self, chan):
        chan = chan.strip("#") + self.suffix
        if chan not in self.backends:
            bpath = path.join(self.prefix, chan)
            self.backends[chan] = KosBackend(bpath, 90, True) 
        return self.backends[chan]

    def help(self, command, args, channel, **kwargs):
        if command == "+1":
            return [(1, kwargs["from_nick"], "!+1 [entity] gives karma to [entity]")]
        if command == "-1":
            return [(1, kwargs["from_nick"], "!-1 [entity] takes karma from [entity]")]
        if command == "karma":
            return [(1, kwargs["from_nick"], "!karma [entity] gives karma for [entity]")]
        if command == "lskarma":
            return [(1, kwargs["from_nick"], "!lskarma lists all karma entities")]
    
    def cmd(self, command, args, channel, **kwargs):
        if command == "+1":
            if args:
                self.backend(channel).positiveKarma(args)
                return [(1, channel, "gave 1 karma to " + args)]
            else:
                return self.help(command, args, channel,**kwargs)

        if command == "-1":
            if args:
                self.backend(channel).negativeKarma(args)
                return [(1, channel, "took 1 karma from " + args)]
            else:
                return self.help(command, args, channel,**kwargs)

        if command == "karma":
            if args:
                ret = "{e} has karma: {k:.3f}".format(e = args, k = self.backend(channel).getKarma(args))
                return [(1, channel, ret)]
            else:
                return self.help(command, args, channel, **kwargs)

        if command == "lskarma":
            karmalist = string.join(self.backend(channel).getAllEntities(), ", ")
            ret = "things that have karma: {}".format(karmalist)
            return [(1, channel, ret)]


    def listen(self, msg, channel, **kwargs):
        for karmatoken in self.reg.findall(msg):
            if karmatoken.startswith("++") or karmatoken.endswith("++"):
                self.backend(channel).positiveKarma(karmatoken.strip("++"))
                
            if karmatoken.startswith("--") or karmatoken.endswith("--"):
                self.backend(channel).negativeKarma(karmatoken.strip("--"))

    def stop(self):
        for be in self.backends.values():
            be.disconnect()
