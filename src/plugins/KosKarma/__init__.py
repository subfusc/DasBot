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
            return [(1, kwargs["from_nick"], "!+1 [thing] gives karma to [thing]")]
        if command == "-1":
            return [(1, kwargs["from_nick"], "!-1 [thing] takes karma from [thing]")]
        if command == "karma":
            return [(1, kwargs["from_nick"], "!karma [thing] gives karma for [thing]")]
        if command == "lskarma":
            return [(1, kwargs["from_nick"], "!lskarma lists all karma things")]
        if command == "hikarma":
            return [(1, kwargs["from_nick"], "!hikarma [n] lists n best things")]
        if command == "lokarma":
            return [(1, kwargs["from_nick"], "!lokarma [n] lists n worst things")]
    
    def cmd(self, command, args, channel, **kwargs):
        if command == "+1":
            if args:
                if args != kwargs['from_nick']:
                    self.backend(channel).positiveKarma(args)
            else:
                return self.help(command, args, channel,**kwargs)

        if command == "-1":
            if args:
                self.backend(channel).negativeKarma(args)
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
            return [(1, channel, "karma things: {}".format(karmalist))]

        if command == "hikarma":
            if args:
                if not args.isdigit():
                    return self.help(command, args, channel, **kwargs)
                best = self.backend(channel).getNBestList(int(args))
            else:
                best = self.backend(channel).getNBestList()
            best = string.join(["{}: {:.3f}".format(e, k) for e,k in best])
            return [(1, channel, "good karma things in {} - {}".format(channel, best))]
                
        if command == "lokarma":
            if args:
                if not args.isdigit():
                    return self.help(command, args, channel, **kwargs)
                worst = self.backend(channel).getNWorstList(int(args))
            else:
                worst = self.backend(channel).getNWorstList()
            worst = string.join(["{}: {:.3f}".format(e, k) for e,k in worst])
            return [(1, channel, "bad karma things in {} - {}".format(channel, worst))]

    def listen(self, msg, channel, **kwargs):
        for karmatoken in self.reg.findall(msg):
            if karmatoken.startswith("++") or karmatoken.endswith("++"):
                if karmatoken.strip("++") != kwargs['from_nick']:
                    self.backend(channel).positiveKarma(karmatoken.strip("++"))
                
            if karmatoken.startswith("--") or karmatoken.endswith("--"):
                self.backend(channel).negativeKarma(karmatoken.strip("--"))

    def stop(self):
        for be in self.backends.values():
            be.disconnect()
