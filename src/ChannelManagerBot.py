# -*- coding: utf-8 -*-
# Basic interface class for keeping track of users in an IRC environment.
# Copyright (C) 2012  Sindre Wetjen

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from IRCbot import IRCbot
from threading import Timer
from GlobalConfig import *

class ChannelManagementBot(IRCbot):

    def __init__(self):
        super(ChannelManagementBot, self).__init__()
        self.channel = {}
        self.nicks = {}

    def cmd(self, command, args, channel, **kwargs):
        if DEBUG: print("ChannelManagementBot CMD function")
        super(ChannelManagementBot, self).cmd(command, args, channel, **kwargs)
        if command == "whos":
            if args in self.channel[channel]:
                self.msg(channel, "[" + ", ".join(self.channel[channel][args]) + "]", to = kwargs['from_nick'])
            else: self.msg(channel, "Illegal key!", to = kwargs['from_nick'])
        
    def management_cmd(self, command, args, **kwargs):
        if command == "MODE":
            self._mode_parse(args, **kwargs)
        elif command == "JOIN":
            self.channel[kwargs["msg"]]["user"].append(kwargs["from_nick"])
            self.nicks[kwargs["from_nick"]] == True
        elif command == "QUIT":
            for c in self.channel:
                self.__rm_user(c, kwargs["from_nick"])
                self.__rm_user_from_nicks(kwargs["from_nick"])
        elif command == "PART":
            self.__rm_user(args, kwargs["msg"])
            if not self.__exists_in_one_channel(args[1]):
                self.__rm_user_from_nicks(args[1])
        elif command == "KICK":
            args = args.split()
            self.__rm_user(args[0], args[1])
            if not self.__exists_in_one_channel(args[1]):
                self.__rm_user_from_nicks(args[1])
        elif command == "NICK":
            self.__change_nick(kwargs["from_nick"], kwargs["msg"])
                
    def manage_users_during_join(self, name, args):
        if not name in self.channel: 
            self.channel[name] = {}
            self.channel[name]['user'] = []
            self.channel[name]['op'] = []
            self.channel[name]['voice'] = []

        nicks = args.split()
        for nick in nicks:
            if nick[0] == "+":
                self.channel[name]['voice'].append(nick[1:])
                self.channel[name]['user'].append(nick[1:])
            elif nick[0] == "@":
                self.channel[name]['op'].append(nick[1:])
                self.channel[name]['user'].append(nick[1:])
            else:
                self.channel[name]['user'].append(nick)
            self.nicks[nick] = True

    def __exists_in_one_channel(self, nick):
        for channel in self.channel:
            if nick in channel["user"]: return True
        return False
            
    def __rm_user(self, channel, nick):
        channel = self.channel[channel]
        if nick in channel["user"]: del(channel["user"][channel["user"].index(nick)])
        if nick in channel["voice"]: del(channel["voice"][channel["voice"].index(nick)])
        if nick in channel["op"]: del(channel["op"][channel["op"].index(nick)])

    def __change_nick(self, from_nick, to_nick): 
        self.__rm_user_from_nick(from_nick)
        self.nicks[to_nick] = True
        self.__change_nick_all_channels(from_nick, to_nick)

    def __change_nick_all_channels(self, from_nick, to_nick): 
        for c in self.channel:
            channel = self.channel[c]
            if from_nick in channel["users"]:
                channel["users"].append(from_nick)
                if from_nick in channel["voice"]:
                    channel["voice"].append(to_nick)
                if from_nick in channel["op"]:
                    channel["op"].append(to_nick)
                self.__rm_user(c, from_nick)
            
    def __rm_user_from_nicks(self, nick):
        del(self.nicks[self.nicks.index(nick)])
            
    def __rm_voice(self, channel, nick):
        channel = self.channel[channel]
        if nick in channel["voice"]: del(channel["voice"][channel["voice"].index(nick)])

    def __rm_op(self, channel, nick):
        channel = self.channel[channel]
        if nick in channel["op"]: del(channel["op"][channel["op"].index(nick)])

    def visible_for_bot(self, nick):
        return nick in self.nicks
            
    def _mode_parse(args, **kwargs):
        args = args.split()
        add = True if args[0][0] == "+" else False
        for x, char in enumerate(args[0][1:]):
            if char == 'o':
                if add: self.channel[args[0]]["op"].append(args[x + 2])
                else: self.__rm_op(args[0], args[x + 2])
            if char == 'v':
                if add: self.channel[args[0]]["voice"].append(args[x + 2])
                else: self.__rm_voice(args[0], args[x + 2])
