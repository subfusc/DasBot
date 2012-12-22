# -*- coding: utf-8 -*- 
# 
# Copyright (C) 2012 Herman Torjussen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://gnu.org/licenses/>.


import GlobalConfig as conf
from time import strftime
from os import makedirs
from os import path
from os import sep

class Plugin(object):

    def __init__(self):
        self.botname = "{n}@{h}".format(n = conf.NAME, h = conf.HOST)
        self.stdformat = "{d} {n}!{i}@{h} {m}\n"
        self.hlpformat = "{d} {n}!{i}@{h} {hc}{cmd} {a}\n"
        self.cmdformat = "{d} {n}!{i}@{h} {cc}{cmd} {a}\n"
        self.dateformat = "[%F %R]"
        self.prefix = "data" + sep + "log"
        self.suffix = ".log"
        self.logs = dict()

        if not path.isdir(self.prefix):
            makedirs(self.prefix)
        
    def listen(self, msg, channel, **kwargs):
        self.logchan(channel, self.stdformat, msg, **kwargs)

    def cmd(self, command, args, channel, **kwargs):
        self.logchan(channel, self.cmdformat, [ command, args ], **kwargs)

    def help(self, command, args, channel, **kwargs):
        self.logchan(channel, self.hlpformat, [ command , args ], **kwargs)

    def stop(self):
        for log in self.logs.values():
            log.close()
    
    def logchan(self, chan, lformat, msg, **kwargs):
        if not chan.startswith("#"):
            return

        if chan not in self.logs:
            logfile = path.join(self.prefix, chan.strip("#") + self.suffix)
            try:
                log = open(logfile, "a", conf.LOG_BUFFER_SIZE)
                self.logs[chan] = log # using dict to handle open fd's
            except IOError as e:
                print "Logger: {}".format(e)
                return

        log = self.logs[chan]

        if lformat == self.stdformat:
            log.write(lformat.format(
                                    d = strftime(self.dateformat),
                                    n = kwargs["from_nick"],
                                    i = kwargs["from_ident"],
                                    h = kwargs["from_host_mask"],
                                    m = msg))
        if lformat == self.cmdformat:
            log.write(lformat.format(
                                    d = strftime(self.dateformat),
                                    n = kwargs["from_nick"],
                                    i = kwargs["from_ident"],
                                    h = kwargs["from_host_mask"],
                                    cmd = msg[0],
                                    a = msg[1],
                                    cc = conf.COMMAND_CHAR))
        if lformat == self.hlpformat:
            log.write(lformat.format(
                                    d = strftime(self.dateformat),
                                    n = kwargs["from_nick"],
                                    i = kwargs["from_ident"],
                                    h = kwargs["from_host_mask"],
                                    cmd = msg[0],
                                    a = msg[1],
                                    hc = conf.HELP_CHAR))
