#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Written by Sindre Wetjen < sindre dot w at gmail dot com >
# License GPLv3
# For full licence see the LICENSE file in the top directory. 
from PluginBot import PluginBot
import GlobalConfig as conf
import sys

class AdminBot(PluginBot):

    def cmd(self, command, args, channel, **kwargs):
        if conf.DEBUG: print("AdminBot cmd")
        super(AdminBot, self).cmd(command, args, channel, **kwargs)
        #if DEBUG: print("Admin Bot Auth: {u} :: {l}".format(u = kwargs["auth_nick"], l = kwargs["auth_level"]))
        if kwargs['auth_level'] > 95:
            if command == 'quit':
                self.exit = True
        if kwargs['auth_level'] >= 60:
            if command == 'op':
                if args:
                    self.op(channel, args)
                else:
                    self.op(channel, kwargs['from_nick'])
            elif command == 'deop':
                self.deop(channel, args)
            elif command == 'join':
                if args[0] == '#':
                    self.join(args.strip())
            elif command == 'part':
                if args == None:
                    self.part(channel)
                elif args[0] == '#':
                    self.part(args.strip())
        if kwargs['auth_level'] >= 30:
            if command == 'voice':
                if args:
                    self.voice(channel, args)
                else:
                    self.voice(channel, kwargs['from_nick'])
            elif command == 'devoice':
                self.devoice(channel, args)
        if command == 'topic':
            if args == None:
                self.msg(channel, kwargs['channel_topic'])
            elif kwargs['auth_level'] >= 30:
                self.topic(channel, args)
        if command == 'version':
            self.msg(channel, "I am in version {ver}".format(ver = kwargs["version"]))
