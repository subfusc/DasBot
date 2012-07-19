#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Written by Sindre Wetjen < sindre dot w at gmail dot com >
# License GPLv3
# For full licence see the LICENSE file in the top directory.
from AdminBot import AdminBot
from GlobalConfig import *
from time import strftime

class LoggerBot(AdminBot):

    def __init__(self):
        super(LoggerBot, self).__init__()
        self.file = open(LOG_FILE, 'a', LOG_BUFFER_SIZE)
        self.file.write("{n} Started at {d}\n".format(n = NAME, d = strftime("[%H:%M %Y/%m/%d]")))
        
    def __del__(self):
        super(LoggerBot, self).__del__()
        self.file.write("{n} Stopped at {d}\n".format(n = NAME, d = strftime("[%H:%M %Y/%m/%d]")))
        self.file.close()
        
    def _server_command(self, command, server):
        if not command == 'PING':
            self.file.write("{d}: {s}:{c}\n".format(d = strftime("[%H:%M %Y/%m/%d]"),
                                                    s = server, c = command))
        super(LoggerBot, self)._server_command(command, server)

    def management_cmd(self, command, args, **kwargs):
        self.file.write("{d}: {n}!{i}@{h}:{c} {a}\n".format(d = strftime("[%H:%M %Y/%m/%d]"),
                                                            n = kwargs['from_nick'],
                                                            i = kwargs['from_ident'],
                                                            h = kwargs['from_host_mask'],
                                                            c = command, a = args))
        super(LoggerBot, self).management_cmd(command, args, **kwargs)
        
    def cmd(self, command, args, channel, **kwargs):
        self.file.write("{t}: {n}!{i}@{h} {c}:{cmd_char}{cmd} {a}\n".format(t = strftime("[%H:%M %Y/%m/%d]"),
                                                                            n = kwargs['from_nick'],
                                                                            i = kwargs['from_ident'],
                                                                            h = kwargs['from_host_mask'],
                                                                            c = channel,
                                                                            cmd = command, a = args,
                                                                            cmd_char = COMMAND_CHAR))
        super(LoggerBot, self).cmd(command, args, channel, **kwargs)

    def listen(self, command, msg, channel, **kwargs):
        self.file.write("{d}: {n}!{i}@{h} {c}:{m}\n".format(d = strftime("[%H:%M %Y/%m/%d]"),
                                                            c = channel,
                                                            n = kwargs['from_nick'],
                                                            i = kwargs['from_ident'],
                                                            h = kwargs['from_host_mask'],
                                                            m = msg))
        super(LoggerBot, self).listen(command, msg, channel, **kwargs)

    def help(self, command, args, channel, **kwargs):
        self.file.write("{d}: {n}!{i}@{h} {c}:{hc}{cmd} {a}\n".format(d = strftime("[%H:%M %Y/%m/%d]"),
                                                                      c = channel,
                                                                      n = kwargs['from_nick'],
                                                                      i = kwargs['from_ident'],
                                                                      h = kwargs['from_host_mask'],
                                                                      hc = HELP_CHAR,
                                                                      cmd = command, a = args))
        super(LoggerBot, self).help(command, args, channel, **kwargs)
