# -*- coding: utf-8 -*-
import re
import string
from kitchen.text.converters import to_bytes, to_unicode
from os import sep
from os import path
from os import makedirs
from KosBackend import KosBackend

class Plugin(object): 

    def __init__(self, *args):
        self.backends = dict()
        self.prefix = "data" + sep + "karma"
        self.suffix = ".karma"
        self.reg = re.compile(r"(\S+\+\+)|(\S+--)|(--\S+)|(\+\+\S+)", re.U)

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
        if command == "karmaprec":
            return [(1, kwargs["from_nick"], "!karmaprec [thing] gives karma for [thing] with more precision")]
        if command == "lskarma":
            return [(1, kwargs["from_nick"], "!lskarma lists all karma things")]
        if command == "highkarma":
            return [(1, kwargs["from_nick"], "!hikarma [n] lists n best things")]
        if command == "high":
            return [(1, kwargs["from_nick"], "!high [n] lists n best things")]
        if command == "lokarma":
            return [(1, kwargs["from_nick"], "!lokarma [n] lists n worst things")]
        if  command == "low":
            return [(1, kwargs["from_nick"], "!low [n] lists n worst things")]
    
    def cmd(self, command, args, channel, **kwargs):
        if command == "+1":
            if args:
                if args != kwargs['from_nick']:
                    self.backend(channel).positiveKarma(to_unicode(args.strip()))
            else:
                return self.help(command, args, channel,**kwargs)

        if command == "-1":
            if args:
                self.backend(channel).negativeKarma(to_unicode(args.strip()))
            else:
                return self.help(command, args, channel,**kwargs)

        if command == "karma_en":
            if args:
                karma = self.backend(channel).getKarma(to_unicode(args.strip()))
                ret = "{e} has karma: {k:.2f} with a total of {p} positive and {n} negative.".format(e = args, k = karma[0], p = karma[1], n = karma[2])
                return [(1, channel, ret)]
            else:
                return self.help(command, args, channel, **kwargs)

        if command == "karma":
            if args:
                karma = self.backend(channel).getKarma(to_unicode(args.strip()))
                ret = "{e} har karma: {k:.1f} og har fått {p} positive og {n} negative.".format(e = args, k = karma[0], p = karma[1], n = karma[2])
                return [(1, channel, ret)]
            else:
                return self.help(command, args, channel, **kwargs)

        if command == "karmaprec":
            if args:
                karma = self.backend(channel).getKarma(to_unicode(args.strip()))
                ret = "{e} has karma {k:.5f} with a total of {p} positive and {n} negative.".format(e = args, k = karma[0], p = karma[1], n = karma[2])
                return [(1, channel, ret)]
            else:
                return self.help(command, args, channel, **kwargs)

        # if command == "lskarma":
        #     karmalist = string.join([to_bytes(e) for e in self.backend(channel).getAllEntities()], ", ")
        #     return [(1, channel, "karma things: {}".format(karmalist))]

        if command == "hikarma" or command == "high":
            if args:
                if not args.isdigit():
                    return self.help(command, args, channel, **kwargs)
                best = self.backend(channel).getNBestList(int(args))
            else:
                best = self.backend(channel).getNBestList()
            best = string.join(["{}: {:.2f}".format(to_bytes(e), k[0]) for e,k in best])
            return [(1, channel, "good karma things in {} - {}".format(channel, best))]

        if command == "høy" or command == "snill":
            if args:
                if not args.isdigit():
                    return self.help(command, args, channel, **kwargs)
                best = self.backend(channel).getNBestList(int(args))
            else:
                best = self.backend(channel).getNBestList()
            best = string.join(["{}: {:.1f}".format(to_bytes(e), k[0]) for e,k in best])
            return [(1, channel, "Bra karma i {}: {}".format(channel, best))]

        if command == "lav" or command == "slem":
            if args:
                if not args.isdigit():
                    return self.help(command, args, channel, **kwargs)
                worst = self.backend(channel).getNWorstList(int(args))
            else:
                worst = self.backend(channel).getNWorstList()
            worst = string.join(["{}: {:.1f}".format(to_bytes(e), k[0]) for e,k in worst])
            return [(1, channel, "Dårlig karma i {}: {}".format(channel, worst))]

        if command == "lokarma" or command == "low":
            if args:
                if not args.isdigit():
                    return self.help(command, args, channel, **kwargs)
                worst = self.backend(channel).getNWorstList(int(args))
            else:
                worst = self.backend(channel).getNWorstList()
            worst = string.join(["{}: {:.2f}".format(to_bytes(e), k[0]) for e,k in worst])
            return [(1, channel, "bad karma things in {} - {}".format(channel, worst))]

    def listen(self, msg, channel, **kwargs):
        for karmatoken in self.reg.findall(msg):
            match = [x for x in karmatoken if x != ""][0]
            if match.startswith("++") or match.endswith("++"):
                if match.strip("++") != kwargs['from_nick']:
                    self.backend(channel).positiveKarma(to_unicode(match.strip("++")))
                
            if match.startswith("--") or match.endswith("--"):
                self.backend(channel).negativeKarma(to_unicode(match.strip("--")))

    def stop(self):
        for be in self.backends.values():
            be.disconnect()
