import re
import string
from KosBackend import KosBackend

class Plugin(object): 

    def __init__(self):
        self.be = KosBackend("test", 90, True)
        self.reg = re.compile(r"(\w+\+\+|\w+--|\+\+\w+|--\w+)", re.UNICODE)

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
                self.be.positiveKarma(args)
                return [(1, channel, "gave 1 karma to " + args)]
            else:
                return self.help(command, args, channel,**kwargs)

        if command == "-1":
            if args:
                self.be.negativeKarma(args)
                return [(1, channel, "took 1 karma from " + args)]
            else:
                return self.help(command, args, channel,**kwargs)

        if command == "karma":
            if args:
                ret = "{e} has karma: {k:.3f}".format(e = args, k = self.be.getKarma(args))
                return [(1, channel, ret)]
            else:
                return self.help(command, args, channel, **kwargs)

        if command == "lskarma":
            karmalist = string.join(self.be.getAllEntities(), ", ")
            ret = "things that have karma: {}".format(karmalist)
            return [(1, channel, ret)]


    def listen(self, msg, channel, **kwargs):
        for karmatoken in self.reg.findall(msg):
            if karmatoken.startswith("++") or karmatoken.endswith("++"):
                self.be.positiveKarma(karmatoken.strip("++"))
                
            if karmatoken.startswith("--") or karmatoken.endswith("--"):
                self.be.negativeKarma(karmatoken.strip("--"))

    def stop(self):
        self.be.disconnect()
