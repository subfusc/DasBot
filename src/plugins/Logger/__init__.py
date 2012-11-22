# -*- coding: utf-8 -*- 
from GlobalConfig import *
from time import strftime
from os import path

class Plugin(object):

    def __init__(self):
        self.botname= "{n}@{h}".format(n = NAME, h = HOST)
        self.dateformat = "[%F %R]"
        self.prefix = "data/log/"
        
    def listen(self, msg, channel, **kwargs):
        if LOG_CHANNELS:
            self.logchan(channel, msg, **kwargs)
        
    def logchan(self, chan, msg, **kwargs):
        if not chan.startswith("#"):
            print "not real channel"
            return
        logf = path.join(self.prefix, chan.strip("#"))
        print "LOGFILE: "+logf
        try:
            f = open(logf, "a", LOG_BUFFER_SIZE)
        except IOError as e:
            print e
            print "logfile "+logf+"does not exist -- open it"
            return
        f.write("{d} {n}!{i}@{h} {m}\n".format(d = strftime(self.dateformat),
                                                c = chan,
                                                n = kwargs['from_nick'],
                                                i = kwargs['from_ident'],
                                                h = kwargs['from_host_mask'],
                                                m = msg))
        f.close()

