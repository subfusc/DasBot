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

import GlobalConfig as conf
from CronBot import CronBot
from threading import Timer
from sys import stderr

class ChannelManagementBot(CronBot):

    def __init__(self):
        super(ChannelManagementBot, self).__init__()
        self.channel = {}
        self.nicks = []
        self.topics = {}

    def cmd(self, command, args, channel, **kwargs):
        if conf.DEBUG: print("ChannelManagementBot CMD function")
        kwargs["channel_users"] = self.channel[channel] if channel in self.channel else [kwargs['from_nick']]
        kwargs["channel_topic"] = self.topics[channel] if channel in self.channel else "Private channel"
        super(ChannelManagementBot, self).cmd(command, args, channel, **kwargs)
        if command == "here":
            self.msg(channel, "[" + ", ".join(self.channel[channel]) + "]", to = kwargs['from_nick'])

    def listen(self, command, line, channel, **kwargs):
        kwargs["channel_users"] = self.channel[channel] if channel in self.channel else [kwargs['from_nick']]
        super(ChannelManagementBot, self).listen(command, line, channel, **kwargs)
        
    def management_cmd(self, command, args, **kwargs):
        super(ChannelManagementBot, self).management_cmd(command, args, **kwargs)
        if conf.IRC_DEBUG: stderr.write(":CHANNEL MANAGEMENT: MANAGEMENT_CMD : {d}\n".format(d=command))
        if command == "JOIN":
            self.channel[kwargs["msg"]].append(kwargs["from_nick"])
            self.nicks.append(kwargs["from_nick"])
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
        elif command == "TOPIC":
            self.__change_topic(args, kwargs["msg"])
        if conf.IRC_DEBUG: stderr.write(":CHANNEL MANAGEMENT: MANAGEMENT_CMD_DONE\n".format())
                
    def manage_users_during_join(self, name, args):
        if conf.VERBOSE: print(":JOIN CHANNEL: Channel: " + name + " Args: " + args + "\n")
        if not name in self.channel: 
            self.channel[name] = []

        nicks = args.split()
        for nick in nicks:
            if nick[0] == "+":
                self.channel[name].append(nick[1:])
                self.nicks.append(nick[1:])
            elif nick[0] == "@":
                self.channel[name].append(nick[1:])
                self.nicks.append(nick[1:])
            else:
                self.channel[name].append(nick)
                self.nicks.append(nick)

    def manage_topic_during_join(self, channel, topic):
        self.__change_topic(channel, topic)
                
    def __exists_in_one_channel(self, nick):
        for channel in self.channel:
            if nick in channel: return True
        return False
            
    def __rm_user(self, channel, nick):
        channel = self.channel[channel]
        if nick in channel: del(channel[channel.index(nick)])

    def __change_nick(self, from_nick, to_nick): 
        self.__rm_user_from_nicks(from_nick)
        self.nicks.append(to_nick)
        self.__change_nick_all_channels(from_nick, to_nick)

    def __change_nick_all_channels(self, from_nick, to_nick): 
        for c in self.channel:
            channel = self.channel[c]
            if from_nick in channel:
                channel.append(from_nick)
                self.__rm_user(c, from_nick)
            
    def __rm_user_from_nicks(self, nick):
        del(self.nicks[self.nicks.index(nick)])

    def in_channel(self, channel):
        return channel in self.channel

    def reset(self):
        super(ChannelManagementBot, self).reset()
        self.channel = {}
        self.nicks = []
    
    def visible_for_bot(self, nick):
        return nick in self.nicks

    def __change_topic(self, channel, topic):
        print("Setting {c} topic to {t}".format(c = channel, t = topic))
        self.topics[channel] = topic
