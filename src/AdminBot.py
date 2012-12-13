#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Written by Sindre Wetjen < sindre dot w at gmail dot com >
# License GPLv3
# For full licence see the LICENSE file in the top directory. 
from ChannelManagerBot import ChannelManagementBot
from GlobalConfig import *
import sys

class AdminBot(ChannelManagementBot):

    def cmd(self, command, args, channel, **kwargs):
        if DEBUG: print("AdminBot cmd")
        super(AdminBot, self).cmd(command, args, channel, **kwargs)
        #if DEBUG: print("Admin Bot Auth: {u} :: {l}".format(u = kwargs["auth_nick"], l = kwargs["auth_level"]))
        if kwargs['auth_level'] > 95:
            if command == 'quit':
                self.exit = True
        if kwargs['auth_level'] >= 60:
            if command == 'op':
                self.op(channel, args)
            elif command == 'deop':
                self.deop(channel, args)
            elif command == 'join':
                if args[0] == '#':
                    self.join(args)
            elif command == 'part':
                if args == None:
                    self.part(channel)
                elif args[0] == '#':
                    self.part(args.strip())
        if kwargs['auth_level'] >= 30:
            if command == 'voice':
                self.voice(channel, args)
            elif command == 'devoice':
                self.devoice(channel, args)
        
