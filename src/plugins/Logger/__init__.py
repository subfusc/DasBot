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


from GlobalConfig import *
from time import strftime
from os import makedirs
from os import path
from os import sep

class Plugin(object):

    def __init__(self):
        self.botname = "{n}@{h}".format(n = NAME, h = HOST)
        self.stdformat = "{d} {n}!{i}@{h} {m}\n"
        self.hlpformat = "{d} {n}!{i}@{h} {hc}{cmd} {a}\n"
        self.cmdformat = "{d} {n}!{i}@{h} {cc}{cmd} {a}\n"
        self.dateformat = "[%F %R]"
        self.prefix = "data" + sep + "log"
        self.suffix = ".log"
        self.log = None

        if not path.isdir(self.prefix):
            makedirs(self.prefix)
        
    def stop(self):
        if self.log:
            self.log.close()
        
    def listen(self, msg, channel, **kwargs):
        self.logchan(channel, self.stdformat, msg, **kwargs)

    def cmd(self, command, args, channel, **kwargs):
        self.logchan(channel, self.cmdformat, [ command, args ], **kwargs)

    def help(self, command, args, channel, **kwargs):
        self.logchan(channel, self.hlpformat, [ command , args ], **kwargs)
    
    def logchan(self, chan, lformat, msg, **kwargs):
        if not chan.startswith("#"):
            return

        logfile = path.join(self.prefix, chan.strip("#") + self.suffix)

        if not self.log or self.log.name != logfile:
            try:
                self.log = open(logfile, "a", LOG_BUFFER_SIZE)
            except IOError as e:
                print "Logger: {}".format(e)
                return

        
        if lformat == self.stdformat:
            self.log.write(lformat.format(
                                    d = strftime(self.dateformat),
                                    n = kwargs["from_nick"],
                                    i = kwargs["from_ident"],
                                    h = kwargs["from_host_mask"],
                                    m = msg))
        if lformat == self.cmdformat:
            self.log.write(lformat.format(
                                    d = strftime(self.dateformat),
                                    n = kwargs["from_nick"],
                                    i = kwargs["from_ident"],
                                    h = kwargs["from_host_mask"],
                                    cmd = msg[0],
                                    a = msg[1],
                                    cc = COMMAND_CHAR))
        if lformat == self.hlpformat:
            self.log.write(lformat.format(
                                    d = strftime(self.dateformat),
                                    n = kwargs["from_nick"],
                                    i = kwargs["from_ident"],
                                    h = kwargs["from_host_mask"],
                                    cmd = msg[0],
                                    a = msg[1],
                                    hc = HELP_CHAR))
