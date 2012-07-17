#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Written by Sindre Wetjen < sindre dot w at gmail dot com >
# License GPLv3
# For full licence see the LICENSE file in the top directory.
from PluginBot import PluginBot
from GlobalConfig import *

class AdminBot(PluginBot):

    def cmd(self, command, args, channel, **kwargs):
        if DEBUG: print("AdminBot cmd")
        super(AdminBot, self).cmd(command, args, channel, **kwargs)
        if DEBUG: print("Admin Bot Auth: {u} :: {l}".format(u = kwargs["auth_nick"], l = kwargs["auth_level"]))
        if kwargs['auth_level'] >= 80:
            if command == 'op':
                self.op(channel, args)
            elif command == 'deop':
                print("Trying to deop {n}".format(n = args))
                self.deop(channel, args)
            elif command == 'join':
                if args[0] == '#':
                    self.join(args)
            elif command == 'part':
                self.part(channel)
        if kwargs['auth_level'] >= 50:
            if command == 'voice':
                self.voice(channel, args)
            elif command == 'devoice':
                self.voice(channel, args)
